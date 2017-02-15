#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
# import zipfile
import threading
from django.conf import settings
import app_datasets.models as datasets_models
import app_sharkdataadmin.models as admin_models
import sharkdata_core

@sharkdata_core.singleton
class DatasetUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'datasets')
        self._metadata_update_thread = None
        self._generate_archives_thread = None

    def translateDataHeaders(self, data_header, 
                         resource_name = 'translate_headers', 
                         language = 'darwin_core'):
#                        language = 'english'):
        """ """
        return sharkdata_core.ResourcesUtils().translateHeaders(data_header, resource_name, language)
           
    def getDatasetListHeaders(self):
        """ """
        if not self._data_header:
            self._data_header = [
                        'dataset_name', 
                        'datatype', 
                        'version', 
                        'dataset_file_name',
                        #
                        'dwc_archive_available',
                        'dwc_archive_eurobis_available',
                        'dwc_archive_sampledata_available',
                        #
#                         'ftp_file_path', 
#                         'content_data', 
#                         'content_metadata', 
#                         'content_metadata_auto', 
#                         'uploaded_by', 
#                         'uploaded_datetime', 
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
                        'dataset_name': 'Dataset name', 
                        'datatype': 'Datatype', 
                        'version': 'Version', 
                        'dataset_file_name': 'File name',
                        #
                        'dwc_archive_available': 'DwC-Archive available',
                        'dwc_archive_eurobis_available': 'DwC-Archive EurOBIS available',
                        'dwc_archive_sampledata_available': 'DwC-Archive SampleData available',
                        # 
#                         'ftp_file_path': '', 
#                         'content_data': '', 
#                         'content_metadata': '', 
#                         'content_metadata_auto': '', 
#                         'uploaded_by': 'Uploaded by', 
#                         'uploaded_datetime': '', 
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
        data_content = ''
        zipreader = sharkdata_core.SharkArchiveFileReader(db_dataset.dataset_file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            data_content = zipreader.getDataAsText().decode('cp1252') # Default encoding in archive data.

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
        data_content = ''
        zipreader = sharkdata_core.SharkArchiveFileReader(db_dataset.dataset_file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            data_content = zipreader.getDataColumnsAsText().decode('cp1252') # Default encoding in archive data.

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
        concat_metadata = db_dataset.content_metadata + '\n' + db_dataset.content_metadata_auto
        for row in concat_metadata.split('\n'):
            if ':' in row:
                parts = row.split(':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_list.append(key + ': ' + value)
        #
        return '\r\n'.join(metadata_list)
    
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
        """ Delete one version of the dataset from the FTP area. """
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
                if file_name.startswith('SHARK') and file_name.endswith('.zip'):
                    os.remove(file_path)
        #
        return None # No error message.

    def deleteOldFtpVersions(self, logrow_id = None, user = ''):
        """ Delete older versions of the datasets from the FTP area. """
        archive = sharkdata_core.SharkArchive(self._ftp_dir_path)
        for file_name in sorted(archive.getOlderVersionsOfSharkArchiveFilenames()):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                if file_name.startswith('SHARK') and file_name.endswith('.zip'):
                    os.remove(file_path)
        #
        return None # No error message.

    def writeLatestDatasetsInfoToDb(self, logrow_id = None, user = ''):
        """ Updates the database from datasets stored in the FTP area.
            I multiple versions of a dataset are in the FTP area only the latest 
            will be loaded.
        """
        error_counter = 0
        # Remove all db rows. 
        datasets_models.Datasets.objects.all().delete()
        # Get latest datasets from FTP archive.
        archive = sharkdata_core.SharkArchive(self._ftp_dir_path)
        for file_name in sorted(archive.getLatestSharkArchiveFilenames()):
            if logrow_id:
                admin_models.addResultLog(logrow_id, result_log = 'Loading file: ' + file_name + '...')                
            try:
                error_string = self.writeFileInfoToDb(file_name, logrow_id, user)
                if error_string:
                    error_counter += 1 
                    admin_models.addResultLog(logrow_id, result_log = 'ERROR: Failed to load: ' + file_name + '. Error: ' + error_string)
            except Exception as e:
                error_counter += 1 
                admin_models.addResultLog(logrow_id, result_log = 'ERROR: Failed to load: ' + file_name + '. Error: ' + unicode(e))
        #
        return error_counter

    def writeFileInfoToDb(self, file_name, logrow_id = None, user = ''):
        """ Extracts info from the dataset filename and from the zip file content and adds to database. """
        try:
            #
            ftp_file_path = os.path.join(self._ftp_dir_path, file_name)
            # Extract info from file name.
            dataset_name, datatype, version = self.splitFilename(file_name)
            # Extract metadata parts.
            metadata = ''
            metadata_auto = ''
            columndata_available = False
            #
            zipreader = sharkdata_core.SharkArchiveFileReader(file_name, self._ftp_dir_path)
            try:
                zipreader.open()
                #
                try:
                    metadata = zipreader.getMetadataAsText()            
                    encoding = 'cp1252'
                    metadata = unicode(metadata, encoding, 'strict')   
                except Exception as e:
                        admin_models.addResultLog(logrow_id, result_log = 'WARNING: ' + unicode(e))
                #
                try:
                    metadata_auto = zipreader.getMetadataAutoAsText()                       
                    encoding = 'cp1252'
                    metadata_auto = unicode(metadata_auto, encoding, 'strict')
                except Exception as e:
                        admin_models.addResultLog(logrow_id, result_log = 'WARNING: ' + unicode(e))
                #
                columndata_available = zipreader.isDataColumnsAvailable()
            finally:
                zipreader.close()                        
            # Save to db.
            dataset = datasets_models.Datasets(
                          dataset_name = dataset_name,
                          datatype = datatype,
                          version = version,
                          dataset_file_name = file_name,
                          ftp_file_path = ftp_file_path,
                          content_data = 'NOT USED',
                          content_metadata = metadata,
                          content_metadata_auto = metadata_auto,
                          #
                          column_data_available = columndata_available,
                          dwc_archive_eurobis_available = False,
                          dwc_archive_eurobis_file_path = '',
                          )
            dataset.save()
            #
            return None # No error message.
        #
        except Exception as e:
            return unicode(e)                



    def splitFilename(self, file_name):
        """ """
        filename = os.path.splitext(file_name)[0]
        parts = filename.split('version')
        name = parts[0].strip('_').strip()
        version = parts[1].strip('_').strip() if len(parts) > 0 else ''
        #
        parts = filename.split('_')
        datatype = parts[1].strip('_').strip()
        #
        return name, datatype, version
        
#     def generateArchivesForAllDatasetsInThread(self, user):
#         """ """
#         
#         logrow_id = admin_models.createLogRow(command = 'Generate archives (DwC, etc.)', status = 'RUNNING', user = user)
#         try:
#             # Check if generate_archives thread is running.
#             if self._generate_archives_thread:
#                 if self._generate_archives_thread.is_alive():
#                     error_message = u"Generate archives is already running. Please try again later."
#                     admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#                     #
#                     return
#             # Use a thread to relese the user. This will take some time.
#             self._generate_archives_thread = threading.Thread(target = self.generateArchivesForAllDatasets, args=(logrow_id, user, ))
#             self._generate_archives_thread.start()
#         except:
#             error_message = u"Can't generate_archives."
#             admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
#             admin_models.addResultLog(logrow_id, result_log = error_message)
#         #
#         return None # No error message.
#                 
#     def generateArchivesForAllDatasets(self, logrow_id, user):
#         """ """
#         sharkdata_core.ArchiveManager().generateArchivesForAllDatasets(logrow_id, user)
#         
