#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

# import os
# import zipfile
import threading
# from django.conf import settings
# import app_datasets.models as datasets_models
import app_sharkdataadmin.models as admin_models
import sharkdata_core

@sharkdata_core.singleton
class SharkdataAdminUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
#         self._data_header = None
#         self._translations = None
#         self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'datasets')

        self._metadata_update_thread = None
        self._generate_archives_thread = None
        self._update_obs_thread = None
        self._cleanup_obs_thread = None
        self._load_obs_thread = None
        self._update_obs_thread = None
        self._generate_ices_xml_thread = None
        self._validate_ices_xml_thread = None
        
    ##### Datasets #####
    
    # TODO: Not in thread yet.
    
    ##### Archives #####
    
    def generateArchivesForAllDatasetsInThread(self, user):
        """ """
        
        logrow_id = admin_models.createLogRow(command = 'Generate archives (DwC, etc.)', status = 'RUNNING', user = user)
        try:
            # Check if generate_archives thread is running.
            if self._generate_archives_thread:
                if self._generate_archives_thread.is_alive():
                    error_message = u"Generate archives is already running. Please try again later."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    #
                    return
            # Use a thread to relese the user. This will take some time.
            self._generate_archives_thread = threading.Thread(target = self.generateArchivesForAllDatasets, args=(logrow_id, user, ))
            self._generate_archives_thread.start()
        except:
            error_message = u"Can't generate_archives."
            admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
            admin_models.addResultLog(logrow_id, result_log = error_message)
        #
        return None # No error message.
                
    def generateArchivesForAllDatasets(self, logrow_id, user):
        """ """
        sharkdata_core.ArchiveManager().generateArchivesForAllDatasets(logrow_id, user)

    ##### SpeciesObs #####
    
    def updateSpeciesObsInThread(self, log_row_id):
        """ """
        # Check if update thread is running.
        if self._update_obs_thread:
            if self._update_obs_thread.is_alive():
                return u"Update is already running. Please try again later."
        # Check if load thread is running.
        if self._load_obs_thread:
            if self._load_obs_thread.is_alive():
                return u"Load is already running. Please try again later."              
        # Check if clean up thread is running.
        if self._cleanup_obs_thread:
            if self._cleanup_obs_thread.is_alive():
                return u"Clean up is already running. Please try again later."              
        # Use a thread to relese the user. This task will take some time.
        self._update_obs_thread = threading.Thread(target = sharkdata_core.SpeciesObsUtils().updateSpeciesObs, args=(log_row_id,))
        self._update_obs_thread.start()
        #
        return None # No error message.
         
    def cleanUpSpeciesObsInThread(self, log_row_id):
        """ """
        # Check if update thread is running.
        if self._update_obs_thread:
            if self._update_obs_thread.is_alive():
                return u"Update is already running. Please try again later."
        # Check if load thread is running.
        if self._load_obs_thread:
            if self._load_obs_thread.is_alive():
                return u"Load is already running. Please try again later."              
        # Check if clean up thread is running.
        if self._cleanup_obs_thread:
            if self._cleanup_obs_thread.is_alive():
                return u"Clean up is already running. Please try again later."              
        # Use a thread to relese the user. This task will take some time.
        self._cleanup_obs_thread = threading.Thread(target = sharkdata_core.SpeciesObsUtils().cleanUpSpeciesObs, args=(log_row_id,))
        self._cleanup_obs_thread.start()

        return None # No error message.

    ##### ExportFormats #####
    
    def generateIcesXmlInThread(self, datatype_list, year_from, year_to, status, user):
        """ """
        logrow_id = admin_models.createLogRow(command = 'Generate ICES-XML file.', status = 'RUNNING', user = user)
        try:
            # Check if thread is running.
            if self._generate_ices_xml_thread:
                if self._generate_ices_xml_thread.is_alive():
                    error_message = u"Generate ICES-XML file is already running. Please try again later."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    #
                    return
            # Use a thread to relese the user.
            self._generate_ices_xml_thread = threading.Thread(target = sharkdata_core.GenerateIcesXml().generateIcesXml, 
                                                              args=(logrow_id, datatype_list, year_from, year_to, status, user ))
            self._generate_ices_xml_thread.start()
        except Exception as e:
            error_message = u"Can't generate ICES-XML file." + '\nException: ' + unicode(e) + '\n'
            admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
            admin_models.addResultLog(logrow_id, result_log = error_message)
        #
        return None # No error message.
                 
    def validateIcesXmlInThread(self, datatype_list, user):
        """ """
        logrow_id = admin_models.createLogRow(command = 'Validate ICES-XML file.', status = 'RUNNING', user = user)
        try:
            # Check if thread is running.
            if self._validate_ices_xml_thread:
                if self._validate_ices_xml_thread.is_alive():
                    error_message = u"Validate ICES-XML file is already running. Please try again later."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    #
                    return
            # Use a thread to relese the user.
            self._validate_ices_xml_thread = threading.Thread(target = sharkdata_core.ValidateIcesXml().validateIcesXml, 
                                                              args=(logrow_id, datatype_list, user ))
            self._validate_ices_xml_thread.start()
        except Exception as e:
            error_message = u"Can't validate ICES-XML file." + '\nException: ' + unicode(e) + '\n'
            admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
            admin_models.addResultLog(logrow_id, result_log = error_message)
        #
        return None # No error message.
                 
