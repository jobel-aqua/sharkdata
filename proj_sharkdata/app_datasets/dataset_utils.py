#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import zipfile
import threading
import shark_utils
from django.conf import settings
import app_datasets.models as datasets_models
import app_resources.resources_utils as resources_utils
import app_sharkdataadmin.models as admin_models

# import shark_utils.dwc_archive_utils.misc_utils as misc_utils
# import shark_utils.dwc_archive_utils.biological_data_exchange_util as biological_data_exchange_util

import shark_utils.archive_utils.archive_manager as archive_manager

@shark_utils.singleton
class DatasetUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'datasets')
        self._metadata_update_thread = None
        self._generate_archives_thread = None

    def translateDataHeaders(self, data_header, 
                         resource_name = u'translate_headers', 
                         language = u'darwin_core'):
#                        language = u'english'):
        """ """
        return resources_utils.ResourcesUtils().translateHeaders(data_header, resource_name, language)
           
    def getDatasetListHeaders(self):
        """ """
        if not self._data_header:
            self._data_header = [
                        u'dataset_name', 
                        u'datatype', 
                        u'version', 
                        u'dataset_file_name',
                        #
                        u'dwc_archive_available',
                        u'dwc_archive_eurobis_available',
                        u'dwc_archive_sampledata_available',
                        #
#                         u'ftp_file_path', 
#                         u'content_data', 
#                         u'content_metadata', 
#                         u'content_metadata_auto', 
#                         u'uploaded_by', 
#                         u'uploaded_datetime', 
                        ]
        #
        return self._data_header

    def translateDatasetListHeaders(self, data_header, language = None):
        """ """
#         if not language:
#             return data_header
        #
        translated = []
        #
        if not self._translations:
            self._translations = {
                        u'dataset_name': u'Dataset name', 
                        u'datatype': u'Datatype', 
                        u'version': u'Version', 
                        u'dataset_file_name': u'File name',
                        #
                        u'dwc_archive_available': u'DwC-Archive available',
                        u'dwc_archive_eurobis_available': u'DwC-Archive EurOBIS available',
                        u'dwc_archive_sampledata_available': u'DwC-Archive SampleData available',
                        # 
#                         u'ftp_file_path': u'', 
#                         u'content_data': u'', 
#                         u'content_metadata': u'', 
#                         u'content_metadata_auto': u'', 
#                         u'uploaded_by': u'Uploaded by', 
#                         u'uploaded_datetime': u'', 
                        }            
        #
        for item in data_header:
            if item in self._translations:
                translated.append(self._translations[item])
            else:
                translated.append(item)
        #
        return translated

    def getDataAsText(self, dataset_name):
        """ Data is not stored in database, get from zip file."""
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        #
        # Extract data part.
        data_content = u''
        zipreader = shark_utils.SharkArchiveFileReader(db_dataset.dataset_file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            data_content = zipreader.getDataAsText().decode(u'cp1252') # Default encoding in archive data.

        finally:
            zipreader.close()                        
#             print(data_content)
        #
        return data_content
    
    def getDataColumnsAsText(self, dataset_name):
        """ Data is not stored in database, get from zip file."""
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        #
        # Extract data part.
        data_content = u''
        zipreader = shark_utils.SharkArchiveFileReader(db_dataset.dataset_file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            data_content = zipreader.getDataColumnsAsText().decode(u'cp1252') # Default encoding in archive data.

        finally:
            zipreader.close()                        
#             print(data_content)
        #
        return data_content
    
    def getMetadataAsText(self, dataset_name):
        """ """
        db_dataset = datasets_models.Datasets.objects.get(dataset_name=dataset_name)
        # Fix line breaks for windows. Remove rows with no key-value-pairs.
        metadata_list = []
        concat_metadata = db_dataset.content_metadata + u'\n' + db_dataset.content_metadata_auto
        for row in concat_metadata.split(u'\n'):
            if u':' in row:
                parts = row.split(u':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_list.append(key + u': ' + value)
        #
        return u'\r\n'.join(metadata_list)
    
    def saveUploadedFileToFtp(self, uploaded_file):
        """ Note: The parameter 'uploaded_file must' be of class UploadedFile. """
        file_name = unicode(uploaded_file)
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Save by reading/writing chunks..
        destination = open(file_path, 'wb+')
        try:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        finally:
            destination.close()
        return None # No error message.

    def deleteFileFromFtp(self, file_name):
        """ Delete all version of the dataset. """
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Delete the file.
        os.remove(file_path)
        #
        return None # No error message.

    def deleteAllFilesFromFtp(self):
        """ Delete all datasets from FTP area. """
        for file_name in os.listdir(self._ftp_dir_path):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                if file_name.startswith(u'SHARK') and file_name.endswith(u'.zip'):
                    os.remove(file_path)
        #
        return None # No error message.

    def writeLatestDatasetsInfoToDb(self, logrow_id = None, user = u''):
        """ Updates the database from datasets stored in the FTP area.
            I multiple versions of a dataset are in the FTP area only the latest 
            will be loaded.
        """
        error_counter = 0
        # Remove all db rows. 
        datasets_models.Datasets.objects.all().delete()
        # Get latest datasets from FTP archive.
        archive = shark_utils.SharkArchive(self._ftp_dir_path)
        for file_name in sorted(archive.getLatestSharkArchiveFilenames()):
            if logrow_id:
                admin_models.addResultLog(logrow_id, result_log = u'Loading file: ' + file_name + u'...')                
            try:
                self.writeFileInfoToDb(file_name, user)
            except Exception as e:
                error_counter += 1 
                admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to load: ' + file_name + u'.')                
        #
        return error_counter

    def writeFileInfoToDb(self, file_name, user = u''):
        """ Extracts info from the dataset filename and from the zip file content and adds to database. """
        #
        ftp_file_path = os.path.join(self._ftp_dir_path, file_name)
        # Extract info from file name.
        dataset_name, datatype, version = self.splitFilename(file_name)
        # Extract metadata parts.
        metadata = u''
        metadata_auto = u''
        zipreader = shark_utils.SharkArchiveFileReader(file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            metadata = zipreader.getMetadataAsText()            
            encoding = u'cp1252'
            metadata = unicode(metadata, encoding, 'strict')
            metadata_auto = zipreader.getMetadataAutoAsText()                       
            encoding = u'cp1252'
            metadata_auto = unicode(metadata_auto, encoding, 'strict')
            #
            columndata_available = zipreader.isDataColumnsAvailable()
        finally:
            zipreader.close()                        
#             print(metadata_auto)
        # Save to db.
        
        
###        print(u'DEBUG: Save to database: ' +  dataset_name)
        
        
        dataset = datasets_models.Datasets(
                      dataset_name = dataset_name,
                      datatype = datatype,
                      version = version,
                      dataset_file_name = file_name,
                      ftp_file_path = ftp_file_path,
                      content_data = u'NOT USED',
                      content_metadata = metadata,
                      content_metadata_auto = metadata_auto,
                      #
                      column_data_available = columndata_available,
                      dwc_archive_eurobis_available = False,
                      dwc_archive_eurobis_file_path = u'',
                      )
        dataset.save()
        #
        return None # No error message.

    def splitFilename(self, file_name):
        """ """
        filename = os.path.splitext(file_name)[0]
        parts = filename.split(u'version')
        name = parts[0].strip(u'_').strip()
        version = parts[1].strip(u'_').strip() if len(parts) > 0 else u''
        #
        parts = filename.split(u'_')
        datatype = parts[1].strip(u'_').strip()
        #
        return name, datatype, version
        
#     def updateMetadataForAllDatasetsInThread(self, user):
#         """ """
#         logrow_id = admin_models.createLogRow(command = u'Update metadata for all datasets', status = u'RUNNING', user = user)
#         try:
#             # Check if metadata update thread is running.
#             if self._metadata_update_thread:
#                 if self._metadata_update_thread.is_alive():
#                     error_message = u"Metadata update is already running. Please try again later."
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#                     #
#                     return
#             # Use a thread to relese the user. This will take some time.
#             self._metadata_update_thread = threading.Thread(target = self.updateMetadataForAllDatasets, args=(logrow_id, user, ))
#             self._metadata_update_thread.start()
#         except:
#             error_message = u"Failed to update metadata."
#             admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#             admin_models.addResultLog(logrow_id, result_log = error_message)
#         #
#         return None # No error message.
#                 
#     def updateMetadataForAllDatasets(self, logrow_id, user):
#         """ """
#         error_counter = 0
#         archive = shark_utils.SharkArchive(self._ftp_dir_path)
#         for file_name in sorted(archive.getLatestSharkArchiveFilenames()):
#             admin_models.addResultLog(logrow_id, result_log = u'Updating metadata for: ' + file_name + u'...')
#             try:
#                 zipwriter = shark_utils.SharkArchiveFileWriter(file_name, self._ftp_dir_path)
#                 zipwriter.generateMetadataAuto()
#             except Exception as e:
#                 error_counter += 1 
#                 admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to update metadata in: ' + file_name + u'.')                
#         # Update database when finished.
#         admin_models.addResultLog(logrow_id, result_log = u'\nReload all datasets from FTP to DB.\n')
#         self.writeLatestDatasetsInfoToDb(logrow_id, user)
#         #
#         if error_counter > 0:
#             admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED (Errors: ' + unicode(error_counter) + u')')
#         else:
#             admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
        
    def generateArchivesForAllDatasetsInThread(self, user):
        """ """
        
        logrow_id = admin_models.createLogRow(command = u'Generate archives (DwC, etc.)', status = u'RUNNING', user = user)
        try:
            # Check if generate_archives thread is running.
            if self._generate_archives_thread:
                if self._generate_archives_thread.is_alive():
                    error_message = u"Generate archives is already running. Please try again later."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    #
                    return
            # Use a thread to relese the user. This will take some time.
            self._generate_archives_thread = threading.Thread(target = self.generateArchivesForAllDatasets, args=(logrow_id, user, ))
            self._generate_archives_thread.start()
        except:
            error_message = u"Can't generate_archives."
            admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
            admin_models.addResultLog(logrow_id, result_log = error_message)
        #
        return None # No error message.
                
    def generateArchivesForAllDatasets(self, logrow_id, user):
        """ """
        
        
        archive_manager.ArchiveManager().generateArchivesForAllDatasets(logrow_id, user)
        
        
#         # Load resource file containing WoRMS info for taxa.
#         worms_info_object = misc_utils.SpeciesWormsInfo()
#         worms_info_object.loadSpeciesFromResource(u'taxa_worms_info')
#         
#         error_counter = 0
# #         archive = shark_utils.SharkArchive(self._ftp_dir_path)
# #         for zip_file_name in sorted(archive.getLatestSharkArchiveFilenames()):
#         datasets = models.Datasets.objects.all()
#         for dataset in datasets:
#             zip_file_name = dataset.dataset_file_name
#             
#             # === Test for some datatypes only. ===
#             datatype = u''
#             dwca_config_dir = u''
#             if zip_file_name.startswith(u'SHARK_Zooplankton'):
#                 datatype = u'Zooplankton'
#                 dwca_config_dir = u'config_files/zooplankton'
#             elif zip_file_name.startswith(u'SHARK_Phytoplankton'):
#                 datatype = u'Phytoplankton'
#                 dwca_config_dir = u'config_files/phytoplankton'
#             elif zip_file_name.startswith(u'SHARK_Zoobenthos'):
#                 datatype = u'Zoobenthos'
#                 dwca_config_dir = u'config_files/zoobenthos'
#             else:
#                 continue # Only ZP.
# 
#             # === Test for GBIF-Occurrence, GBIF-EurOBIS (EMODnet-Bio) and GBIF for Sample Data. ===
#             admin_models.addResultLog(logrow_id, result_log = u'Generating archive file for: ' + zip_file_name + u'...')
#             try:
#                 dataset = misc_utils.Dataset()
#                 dataset.loadDataFromZipFile(zip_file_name,
#                                             dataset_dir_path = self._ftp_dir_path,
#                                             encoding = u'cp1252')
# 
#                 # === Test for GBIF-Occurrence. ===
#                 try:
#                     admin_models.addResultLog(logrow_id, result_log = u'   - Darwin Core Archive.')
#                     archive = biological_data_exchange_util.DarwinCoreArchiveFormat(
#                                                                             datatype, 
#                                                                             u'settings_dwca.json',
#                                                                             dwca_config_dir,
#                                                                             meta_file_name = u'meta.xml',
#                                                                             eml_file_name = u'eml.xml',
#                                                                             worms_info_object = worms_info_object)
#                     archive.createArchiveParts(dataset)
#                     # Save generated archive file.
#                     generated_archives_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'generated_archives')
#                     achive_file_name = zip_file_name.replace(u'.zip', u'_DwC-A.zip')
#                     if not os.path.exists(generated_archives_path):
#                         os.makedirs(generated_archives_path)
#                     archive.saveToArchiveFile(achive_file_name, zip_dir_path = generated_archives_path, 
#                                               settings_dir_path = dwca_config_dir)
#                     # Update database.
#                     db_dataset = models.Datasets.objects.get(dataset_file_name = zip_file_name)
#                     db_dataset.dwc_archive_available = True
#                     db_dataset.dwc_archive_file_path = os.path.join(generated_archives_path, achive_file_name)
#                     db_dataset.save()
#                 except Exception as e:
#                     error_counter += 1 
#                     admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate DwC-A from: ' + zip_file_name + u'.')                
#     
#                 # === Test for GBIF-EurOBIS (EMODnet-Bio). ===
#                 try:
#                     admin_models.addResultLog(logrow_id, result_log = u'   - Darwin Core Archive (EurOBIS format).')
#                     archive = biological_data_exchange_util.DarwinCoreArchiveFormatForEurObis(
#                                                                             datatype, 
#                                                                             u'settings_dwca_eurobis.json',
#                                                                             dwca_config_dir,
#                                                                             meta_file_name = u'meta_eurobis.xml',
#                                                                             eml_file_name = u'eml_eurobis.xml',
#                                                                             worms_info_object = worms_info_object)
#                     archive.createArchiveParts(dataset)
#                     # Save generated archive file.
#                     generated_archives_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'generated_archives')
#                     achive_file_name = zip_file_name.replace(u'.zip', u'_DwC-A-EurOBIS.zip')
#                     if not os.path.exists(generated_archives_path):
#                         os.makedirs(generated_archives_path)
#                     archive.saveToArchiveFile(achive_file_name, zip_dir_path = generated_archives_path, 
#                                               settings_dir_path = dwca_config_dir)
#                     # Update database.
#                     db_dataset = models.Datasets.objects.get(dataset_file_name = zip_file_name)
#                     db_dataset.dwc_archive_eurobis_available = True
#                     db_dataset.dwc_archive_eurobis_file_path = os.path.join(generated_archives_path, achive_file_name)
#                     db_dataset.save()
#                 except Exception as e:
#                     error_counter += 1 
#                     print(e)
#                     admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate DwC-A (eurOBIS format) from: ' + zip_file_name + u'.')                
#     
#                 # === Test for GBIF for Sample Data. ===
#                 try:
#                     admin_models.addResultLog(logrow_id, result_log = u'   - Darwin Core Archive (Sample data format).')
#                     archive = biological_data_exchange_util.DarwinCoreArchiveFormatForSampleData(
#                                                                             datatype, 
#                                                                             u'settings_dwca_sampledata.json',
#                                                                             dwca_config_dir,
#                                                                             meta_file_name = u'meta_sampledata.xml',
#                                                                             eml_file_name = u'eml_sampledata.xml',
#                                                                             worms_info_object = worms_info_object)
#                     archive.createArchiveParts(dataset)
#                     # Save generated archive file.
#                     generated_archives_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'generated_archives')
#                     achive_file_name = zip_file_name.replace(u'.zip', u'_DwC-A-SampleData.zip')
#                     if not os.path.exists(generated_archives_path):
#                         os.makedirs(generated_archives_path)
#                     archive.saveToArchiveFile(achive_file_name, zip_dir_path = generated_archives_path, 
#                                               settings_dir_path = dwca_config_dir)
#                     # Update database.
#                     db_dataset = models.Datasets.objects.get(dataset_file_name = zip_file_name)
#                     db_dataset.dwc_archive_sampledata_available = True
#                     db_dataset.dwc_archive_sampledata_file_path = os.path.join(generated_archives_path, achive_file_name)
#                     db_dataset.save()
#                 except Exception as e:
#                     error_counter += 1 
#                     admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate DwC-A (Sample data format) from: ' + zip_file_name + u'.')                
#     
#                 
#             except Exception as e:
#                 error_counter += 1 
#                 admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate archive files from: ' + zip_file_name + u'.')                
#     
#         #
#         if error_counter > 0:
#             admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED (Errors: ' + unicode(error_counter) + u')')
#         else:
#             admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')


