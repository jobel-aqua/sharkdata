#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# import os
import time
import threading
import shark_utils
# from django.conf import settings
import app_speciesobs.models as speciesobs_models
import app_datasets.models as datasets_models
# import app_resources.models as resources_models
import app_resources.resources_utils as resources_utils

@shark_utils.singleton
class SpeciesObsUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._header_clean_up = None
        self._update_obs_thread = None
        self._load_obs_thread = None
        self._cleanup_obs_thread = None

    def getHeaders(self):
        """ """
        if not self._data_header:
            self._data_header = [
                    u'occurrence_id',
                    #
                    u'data_type', 
                    u'scientific_name', 
                    u'scientific_authority', 
                    u'latitude_dd', 
                    u'longitude_dd', 
                    u'sampling_date', 
                    u'sampling_year', 
                    u'sampling_month', 
                    u'sampling_day', 
                    u'sample_min_depth', 
                    u'sample_max_depth', 
                    u'sampler_type', 
                    u'dyntaxa_id', 
                    u'taxon_kingdom', 
                    u'taxon_phylum', 
                    u'taxon_class', 
                    u'taxon_order', 
                    u'taxon_family', 
                    u'taxon_genus', 
                    u'taxon_species', 
                    u'orderer', 
                    u'reporting_institute', 
                    u'sampling_laboratory', 
                    u'analytical_laboratory',                     
                    u'dataset_name',
                    u'dataset_file_name',
                    #
                    u'status', # Used by SLU.
#                     u'last_update_date', # Used for internal purposes, may be external in the future.
#                     u'last_status_change_date', # Not used now, but can be used in the future.

                    ]
        #
        return self._data_header

    def translateHeaders(self, data_header, 
                         resource_name = u'translate_speciesobs_headers', 
                          language = u'darwin_core'):
#                         language = u'english'):
        """ """
        return resources_utils.ResourcesUtils().translateHeaders(data_header, resource_name, language)
           
    def cleanUpHeader(self, data_header):
        """ Internal columns names from SHARKweb etc. are not stable yet. Replace old style with better style. """
        new_header = []
        #
        if not self._header_clean_up:
            self._header_clean_up = {
                    u'data_type_code': u'data_type', 
                    u'used_taxon_name': u'scientific_name', 
                    u'taxon_author': u'scientific_authority', 
                    u'lat_dd': u'latitude_dd', 
                    u'long_dd': u'longitude_dd', 
                    u'visit_date': u'sampling_date', 
                    u'visit_year': u'sampling_year', 
                    u'visit_month': u'sampling_month', 
                    u'visit_day': u'sampling_day', 
                    u'sample_min_depth': u'sample_min_depth', 
                    u'sample_max_depth': u'sample_max_depth', 
                    u'sampler_type_code': u'sampler_type', 
                    u'variable.taxon_id': u'dyntaxa_id', 
                    u'taxon_id': u'dyntaxa_id', 
                    u'taxon_kingdom': u'taxon_kingdom', 
                    u'taxon_phylum': u'taxon_phylum', 
                    u'taxon_class': u'taxon_class', 
                    u'taxon_order': u'taxon_order', 
                    u'taxon_family': u'taxon_family', 
                    u'taxon_genus': u'taxon_genus', 
                    u'taxon_species': u'taxon_species', 
                    u'orderer': u'orderer', 
                    u'reporting_institute_code': u'reporting_institute', 
                    u'sampling_laboratory_code': u'sampling_laboratory', 
                    u'analytical_laboratory_code': u'analytical_laboratory',   
                }            
        #
        for item in data_header:
            if item in self._header_clean_up:
                new_header.append(self._header_clean_up[item])                
            else:
                new_header.append(item)
        #
        return new_header



    def updateSpeciesObsInThread(self):
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
        self._update_obs_thread = threading.Thread(target = self.updateSpeciesObs)
        self._update_obs_thread.start()
        return None # No error message.
         
    def updateSpeciesObs(self):
        """ """
        """ """
#         # Remove all db rows. 
#         speciesobs_models.SpeciesObs.objects.all().delete()
        #
        print(u'Species observations update. Started.')
        
        speciesobs_models.SpeciesObs.objects.all().update(last_update_date = u'0000-00-00')

        
        
        # Loop over all datasets.
#         for dataset_queryset in datasets_models.Datasets.objects.filter(datatype = u'Speciesobs'):
        for dataset_queryset in datasets_models.Datasets.objects.all():
            print(u'Loading data from: ' + dataset_queryset.ftp_file_path)
            #
            zipreader = shark_utils.SharkArchiveFileReader(dataset_queryset.ftp_file_path)
            try:
                zipreader.open()
                data = zipreader.getDataAsText()
            finally:
                zipreader.close()                        
            #
            encoding = u'cp1252'
            rowseparator = '\n'
            fieldseparator = '\t'
            #
            data = unicode(data, encoding, 'strict')
            datarows = (item.strip() for item in data.split(rowseparator)) # Generator instead of list.
            #
            for rowindex, datarow in enumerate(datarows):
                #
                if len(datarow) == 0:
                    continue
                #  
                row = [item.strip() for item in datarow.split(fieldseparator)]
                if rowindex == 0:
                    header = row
                else:
                    header = self.cleanUpHeader(header)
                    rowdict = dict(zip(header, row))
                    
                    # Check if position is valid. Skip row if not.
                    lat_dd = rowdict.get(u'latitude_dd', u'').replace(u',', u'.')
                    long_dd = rowdict.get(u'longitude_dd', u'').replace(u',', u'.')
                    if self.isFloat(lat_dd) and self.isFloat(long_dd):
                        if (float(lat_dd) > 70.0) or (float(lat_dd) < 50.0) or (float(long_dd) > 25.0) or (float(long_dd) < 5.0):
                            # Don't add to SpeciesObs if lat_dd/long_dd is outside the box.
                            print(u'Row skipped, position outside box. Latitude: ' + lat_dd + u' Longitude: ' + long_dd)
                            continue
                    else:
                        # Don't add to SpeciesObs if lat_dd/long_dd is invalid.
                        continue
                      
                    speciesobs = speciesobs_models.SpeciesObs(
                        data_type = rowdict.get(u'data_type', u''),
                        scientific_name = rowdict.get(u'scientific_name', u'-') if rowdict.get(u'scientific_name') else u'-', ### scientific_name
                        scientific_authority = rowdict.get(u'scientific_authority', u'-') if rowdict.get(u'scientific_authority') else u'-', ### scientific_name
                        latitude_dd = rowdict.get(u'latitude_dd', u'').replace(u',', u'.'),
                        longitude_dd = rowdict.get(u'longitude_dd', u'').replace(u',', u'.'),
                        sampling_date = rowdict.get(u'sampling_date', u''),
                        sampling_year = rowdict.get(u'sampling_year', u''),
                        sampling_month = rowdict.get(u'sampling_month', u''),
                        sampling_day = rowdict.get(u'sampling_day', u''),
                        sample_min_depth = rowdict.get(u'sample_minimum_depth', u''),
                        sample_max_depth = rowdict.get(u'sample_maximum_depth', u''),
                        dyntaxa_id = rowdict.get(u'dyntaxa_id', u'') if rowdict.get(u'dyntaxa_id') else u'-',
                        taxon_kingdom = rowdict.get(u'taxon_kingdom', u'-') if rowdict.get(u'taxon_kingdom') else u'-',
                        taxon_phylum = rowdict.get(u'taxon_phylum', u'-') if rowdict.get(u'taxon_phylum') else u'-',
                        taxon_class = rowdict.get(u'taxon_class', u'-') if rowdict.get(u'taxon_class') else u'-',
                        taxon_order = rowdict.get(u'taxon_order', u'-') if rowdict.get(u'taxon_order') else u'-',
                        taxon_family = rowdict.get(u'taxon_family', u'-') if rowdict.get(u'taxon_family') else u'-',
                        taxon_genus = rowdict.get(u'taxon_genus', u'-') if rowdict.get(u'taxon_genus') else u'-',
                        taxon_species = rowdict.get(u'taxon_species', u'-') if rowdict.get(u'taxon_species') else u'-',
 
                        orderer = rowdict.get(u'orderer', u'') if rowdict.get(u'orderer') else u'-',
                        reporting_institute = rowdict.get(u'reporting_institute', u'') if rowdict.get(u'reporting_institute') else u'-',
                        sampling_laboratory = rowdict.get(u'sampling_laboratory', u'') if rowdict.get(u'sampling_laboratory') else u'-',
                        analytical_laboratory = rowdict.get(u'analytical_laboratory', u'') if rowdict.get(u'analytical_laboratory') else u'-',
                        #
                        occurrence_id = u'', # Added below.
                        #
                        dataset_name = unicode(dataset_queryset.dataset_name),
                        dataset_file_name = unicode(dataset_queryset.dataset_file_name),
         
                        ##### Example: 'POINT(-73.9869510 40.7560540)', Note: Order longitude - latitude.
                        geometry = 'POINT(' + rowdict.get(u'longitude_dd', u'0.0').replace(u',', u'.') + ' ' + rowdict.get(u'latitude_dd', u'0.0').replace(u',', u'.') + ')',
         
                        )
                    # Calculate DarwinCore Observation Id.
                    generated_occurrence_id = speciesobs.calculateDarwinCoreObservationIdAsMD5()
                    #
#                     if speciesobs_models.SpeciesObs(
#                         speciesobs.save()
                    #speciesobs_models.SpeciesObs.objects.filter(status=u'DELETED').delete()
                    try: 
                        obs_existing_row = speciesobs_models.SpeciesObs.objects.get(occurrence_id = generated_occurrence_id)
                    except:
                        obs_existing_row = None # Does not exist.
                    #
                    current_date = unicode(time.strftime(u'%Y-%m-%d'))
                    #
                    if obs_existing_row:
                        if obs_existing_row.status == u'ACTIVE':
                            obs_existing_row.last_update_date = current_date
                        else:
                            obs_existing_row.status= u'ACTIVE'
                            obs_existing_row.last_update_date = current_date
                            obs_existing_row.last_status_change_date = current_date
                        #    
                        obs_existing_row.save()
                    else:
                        speciesobs.occurrence_id = generated_occurrence_id
                        speciesobs.status = u'ACTIVE'
                        speciesobs.last_update_date = current_date
                        speciesobs.last_status_change_date = current_date
                        #
                        speciesobs.save()
                        
        #
        print(u'Species observations update. Mark not updated rows as DELETED.')
        #
        current_date = unicode(time.strftime(u'%Y-%m-%d'))
#         speciesobs_models.SpeciesObs.objects.filter(last_update_date = u'0000-00-00').update(status = 'DELETED')
#         speciesobs_models.SpeciesObs.objects.filter(last_update_date = u'0000-00-00').update(last_update_date = current_date)
        #
        datarows = speciesobs_models.SpeciesObs.objects.filter(last_update_date = u'0000-00-00')
        for datarow in datarows:
            if datarow.status == u'DELETED':
                datarow.last_update_date = current_date
            else:
                datarow.status = u'DELETED'
                datarow.last_update_date = current_date
                datarow.last_status_change_date = current_date
            #
            datarow.save()
            
        #
        print(u'Species observations update. Finished.')
        
    def isFloat(self, value):
        """ Useful utility. """
        try:
            float(value)
            return True
        except ValueError:
            return False     
    
    def loadSpeciesObsInThread(self):
        """ """
        
        return u"This feature is not implemented yet..."
        
        
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
        self._load_obs_thread = threading.Thread(target = self.loadSpeciesObs)
        self._load_obs_thread.start()
        return None # No error message.
         
    def loadSpeciesObs(self):
        """ """
        print(u'NOT IMPLRMENTED YEY: SpeciesObsUtils.loadSpeciesObs()')
        
                  
    def cleanUpSpeciesObsInThread(self):
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
        self._cleanup_obs_thread = threading.Thread(target = self.cleanUpSpeciesObs)
        self._cleanup_obs_thread.start()
        return None # No error message.
       
    def cleanUpSpeciesObs(self):
        """ """
        #
        speciesobs_models.SpeciesObs.objects.filter(status=u'DELETED').delete()
         
         
    
#     def loadAllSpeciesObsInThread(self):
#         """ """
#         # Check if loading thread is running.
#         if self._load_obs_thread:
#             if self._load_obs_thread.is_alive():
#                 return u"Loading is already running. Please try again later."
#         # Check if history thread is running.
#         if self._history_thread:
#             if self._history_thread.is_alive():
#                 return u"History update is already running. Please try again later."              
#         # Use a thread to relese the user. This will take some time.
#         self._load_obs_thread = threading.Thread(target = self.loadAllSpeciesObs)
#         self._load_obs_thread.start()
#         return None # No error message.
#                 
#     def loadAllSpeciesObs(self):
#         """ """
#         # Remove all db rows. 
#         speciesobs_models.SpeciesObs.objects.all().delete()
#         #
#         # Loop over all datasets where Datatype = Speciesobs.
#         for dataset_queryset in datasets_models.Datasets.objects.filter(datatype = u'Speciesobs'):
#             print(u'Loading data from: ' + dataset_queryset.ftp_file_path)
#          
#             zipreader = shark_utils.SharkArchiveFileReader(dataset_queryset.ftp_file_path)
#             try:
#                 zipreader.open()
# #                 metadata = zipreader.getMetadataAsText()
# #                 metadata_auto = zipreader.getMetadataAutoAsText()
#                 data = zipreader.getDataAsText()
#             finally:
#                 zipreader.close()                        
#         #                     print(metadata_auto)
#         #                     print(data)
#         
#             encoding = u'cp1252'
#             rowseparator = '\n'
#             fieldseparator = '\t'
#             #
#             data = unicode(data, encoding, 'strict')
#         #                 datarows = [item.strip() for item in data.split(rowseparator)]
#             datarows = (item.strip() for item in data.split(rowseparator)) # Generator instead of list.
#             #
#             for rowindex, datarow in enumerate(datarows):
#                 #
#                 if len(datarow) == 0:
#                     continue
#                  
#                 row = [item.strip() for item in datarow.split(fieldseparator)]
#                 if rowindex == 0:
#                     header = row
#                 else:
#                     header = self.cleanUpHeader(header)
#                     rowdict = dict(zip(header, row))
#                      
#                     speciesobs = speciesobs_models.SpeciesObs(
#                         data_type = rowdict.get(u'data_type', u''),
#                         scientific_name = rowdict.get(u'scientific_name', u'-') if rowdict.get(u'scientific_name') else u'-', ### scientific_name
#                         scientific_authority = rowdict.get(u'scientific_authority', u'-') if rowdict.get(u'scientific_authority') else u'-', ### scientific_name
#                         latitude_dd = rowdict.get(u'latitude_dd', u'').replace(u',', u'.'),
#                         longitude_dd = rowdict.get(u'longitude_dd', u'').replace(u',', u'.'),
#                         sampling_date = rowdict.get(u'sampling_date', u''),
#                         sampling_year = rowdict.get(u'sampling_year', u''),
#                         sampling_month = rowdict.get(u'sampling_month', u''),
#                         sampling_day = rowdict.get(u'sampling_day', u''),
#                         sample_min_depth = rowdict.get(u'sample_minimum_depth', u''),
#                         sample_max_depth = rowdict.get(u'sample_maximum_depth', u''),
#                         dyntaxa_id = rowdict.get(u'dyntaxa_id', u'') if rowdict.get(u'dyntaxa_id') else u'-',
#                         taxon_kingdom = rowdict.get(u'taxon_kingdom', u'-') if rowdict.get(u'taxon_kingdom') else u'-',
#                         taxon_phylum = rowdict.get(u'taxon_phylum', u'-') if rowdict.get(u'taxon_phylum') else u'-',
#                         taxon_class = rowdict.get(u'taxon_class', u'-') if rowdict.get(u'taxon_class') else u'-',
#                         taxon_order = rowdict.get(u'taxon_order', u'-') if rowdict.get(u'taxon_order') else u'-',
#                         taxon_family = rowdict.get(u'taxon_family', u'-') if rowdict.get(u'taxon_family') else u'-',
#                         taxon_genus = rowdict.get(u'taxon_genus', u'-') if rowdict.get(u'taxon_genus') else u'-',
#                         taxon_species = rowdict.get(u'taxon_species', u'-') if rowdict.get(u'taxon_species') else u'-',
# 
#                         orderer = rowdict.get(u'orderer', u'') if rowdict.get(u'orderer') else u'-',
#                         reporting_institute = rowdict.get(u'reporting_institute', u'') if rowdict.get(u'reporting_institute') else u'-',
#                         sampling_laboratory = rowdict.get(u'sampling_laboratory', u'') if rowdict.get(u'sampling_laboratory') else u'-',
#                         analytical_laboratory = rowdict.get(u'analytical_laboratory', u'') if rowdict.get(u'analytical_laboratory') else u'-',
#                         #
#                         generated_occurrence_id = u'', # Added below.
#                         #
#                         dataset_name = unicode(dataset_queryset.dataset_name),
#                         dataset_file_name = unicode(dataset_queryset.dataset_file_name),
#         
#                         ##### Example: 'POINT(-73.9869510 40.7560540)', Note: Order longitude - latitude.
#                         geometry = 'POINT(' + rowdict.get(u'longitude_dd', u'0.0').replace(u',', u'.') + ' ' + rowdict.get(u'latitude_dd', u'0.0').replace(u',', u'.') + ')',
#         
#                         )
#                     # Calculate DarwinCore Observation Id.
#                     speciesobs.generated_occurrence_id = speciesobs.calculateDarwinCoreObservationIdAsMD5()
#                     #
#                     speciesobs.save()
#     
#     def historyClear(self):
#         """ """
#         speciesobs_models.OccurrenceIdHistory.objects.all().delete()
#     
#     def historyUpdateInThread(self):
#         """ """
#         # Check if loading thread is running.
#         if self._load_obs_thread:
#             if self._load_obs_thread.is_alive():
#                 return u"Loading is already running. Please try again later."
#         # Check if history thread is running.
#         if self._history_thread:
#             if self._history_thread.is_alive():
#                 return u"History update is already running. Please try again later."              
#         # Use a thread to relese the user. This will take some time.
#         self._history_thread = threading.Thread(target = self.historyUpdate)
#         self._history_thread.start()
#         return None # No error message.
#     
#     def historyUpdate(self):
#         """ """
#         current_date = time.strftime(u'%Y-%m-%d')
#         
#         # Step 1: Check if all obsrevation events are stored in the history table.
#         #         If not, add it with current date.
#         species_rows = speciesobs_models.SpeciesObs.objects.all()
#         #
#         for species_row in species_rows:
#             # Check
#             try: 
#                 history_item = speciesobs_models.OccurrenceIdHistory.objects.get(generated_occurrence_id=species_row.generated_occurrence_id)
#             except:
#                 history_item = None # Does not exist.
#             if not history_item:
#                 history_item = speciesobs_models.OccurrenceIdHistory(
#                     generated_occurrence_id = species_row.generated_occurrence_id,
#                     state = u'ACTIVE',
#                     added_date = current_date,
#                     deleted_date = u'',
#                     )
#                 history_item.save()
#             else:
#                 if history_item.state == u'DELETED':
#                     history_item.state = u'ACTIVE'
#                     history_item.added_date = current_date
#                     history_item.deleted_date = u''
#                     history_item.save()
#         # Step 2: Check the other way. Is all 'active' still available?
#         #         If not, mark it as deleted.
#         history_rows = speciesobs_models.OccurrenceIdHistory.objects.all()
#         #
#         for history_row in history_rows:
#             if history_row.state == u'ACTIVE':
#                 try:
#                     species_item = speciesobs_models.SpeciesObs.objects.get(generated_occurrence_id=history_row.generated_occurrence_id)
#                 except:
#                     species_item = None # Does not exist.
#                 if not species_item:
#                     history_row.state = u'DELETED'
#                     history_row.deleted_date = current_date
#                     history_row.save()


