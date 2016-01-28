#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2015 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import traceback
from django.conf import settings

import shark_utils
import app_datasets.models as models
import app_sharkdataadmin.models as admin_models
# 
import shark_utils.archive_utils.misc_utils as misc_utils
import shark_utils.archive_utils.dwca_eurobis_bacterioplankton as dwca_eurobis_bacterioplankton
import shark_utils.archive_utils.dwca_eurobis_phytoplankton as dwca_eurobis_phytoplankton
import shark_utils.archive_utils.dwca_eurobis_zoobenthos as dwca_eurobis_zoobenthos
import shark_utils.archive_utils.dwca_eurobis_zooplankton as dwca_eurobis_zooplankton

@shark_utils.singleton
class ArchiveManager(object):
    """ Singleton class. """
    
    def __init__(self):
        """ """
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'datasets')
                    
    def generateArchivesForAllDatasets(self, logrow_id, user):
        """ """
        # Load resource file containing WoRMS info for taxa.
        worms_info_object = misc_utils.SpeciesWormsInfo()
        worms_info_object.loadSpeciesFromResource()
        #
        error_counter = 0
        datasets = models.Datasets.objects.all()
        for dataset in datasets:
            zip_file_name = dataset.dataset_file_name
            #
            admin_models.addResultLog(logrow_id, result_log = u'Generating archive file for: ' + zip_file_name + u'...')
            
            if settings.DEBUG:
                print(u'DEBUG: ===== Processing: ' + zip_file_name)            
            
            #
            archive = None
            dwca_config_dir = u''
            if zip_file_name.startswith(u'SHARK_Zooplankton'):
                archive = dwca_eurobis_zooplankton.DwcaEurObisZooplankton()
            elif zip_file_name.startswith(u'SHARK_Phytoplankton'):
                archive = dwca_eurobis_phytoplankton.DwcaEurObisPhytoplankton()
            elif zip_file_name.startswith(u'SHARK_Zoobenthos'):
                archive = dwca_eurobis_zoobenthos.DwcaEurObisZoobenthos()
            elif zip_file_name.startswith(u'SHARK_Bacterioplankton'): 
                archive = dwca_eurobis_bacterioplankton.DwcaEurObisBacterioplankton()
            #
            if not archive:
                continue # Skip if other datatypes.

            # === Test for GBIF-Occurrence, GBIF-EurOBIS (EMODnet-Bio) and GBIF for Sample Data. ===
            try:
                dataset = misc_utils.Dataset()
                dataset.loadDataFromZipFile(zip_file_name,
                                            dataset_dir_path = self._ftp_dir_path,
                                            encoding = u'cp1252')

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
    
                # === Test for GBIF-EurOBIS (EMODnet-Bio). ===
                try:
                    admin_models.addResultLog(logrow_id, result_log = u'   - Darwin Core Archive (EurOBIS format).')
#                     archive = biological_data_exchange_util.DarwinCoreArchiveFormatForEurObis(
#                                                                             datatype, 
#                                                                             u'settings_dwca_eurobis.json',
#                                                                             dwca_config_dir,
#                                                                             meta_file_name = u'meta_eurobis.xml',
#                                                                             eml_file_name = u'eml_eurobis.xml',
#                                                                             worms_info_object = worms_info_object)
                    # Update database before.
                    db_dataset = models.Datasets.objects.get(dataset_file_name = zip_file_name)
                    db_dataset.dwc_archive_eurobis_available = False
                    db_dataset.dwc_archive_eurobis_file_path = u''
                    db_dataset.save()
                    
                    if worms_info_object:
                        archive.setWormsInfoObject(worms_info_object)
                    #    
                    archive.createArchiveParts(dataset)
                    # Save generated archive file.
                    generated_archives_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'generated_archives')
                    achive_file_name = zip_file_name.replace(u'.zip', u'_DwC-A-EurOBIS.zip')
                    if not os.path.exists(generated_archives_path):
                        os.makedirs(generated_archives_path)
                    archive.saveToArchiveFile(achive_file_name, zip_dir_path = generated_archives_path, 
                                              settings_dir_path = dwca_config_dir)
                    # Update database after.
                    db_dataset = models.Datasets.objects.get(dataset_file_name = zip_file_name)
                    db_dataset.dwc_archive_eurobis_available = True
                    db_dataset.dwc_archive_eurobis_file_path = os.path.join(generated_archives_path, achive_file_name)
                    db_dataset.save()
                except Exception as e:
                    error_counter += 1 
                    print(e)
                    admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate DwC-A (eurOBIS format) from: ' + zip_file_name + u'.')                
    
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
    
                
            except Exception as e:
                error_counter += 1 
                traceback.print_exc()
                admin_models.addResultLog(logrow_id, result_log = u'ERROR: Failed to generate archive files from: ' + zip_file_name + u'.')                
    
        #
        if error_counter > 0:
            admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED (Errors: ' + unicode(error_counter) + u')')
        else:
            admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')

        if settings.DEBUG:
            print(u'DEBUG: Archive generation FINISHED')            

