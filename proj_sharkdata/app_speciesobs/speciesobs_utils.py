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
import app_sharkdataadmin.models as admin_models
#
import shark_utils.archive_utils.misc_utils as misc_utils

@shark_utils.singleton
class SpeciesObsUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._header_cleanup = None
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
#                        language = u'english'):
        """ """
        return resources_utils.ResourcesUtils().translateHeaders(data_header, resource_name, language)
           
    def cleanUpHeader(self, data_header):
        """ Internal columns names from SHARKweb etc. are not stable yet. Replace old style with better style. """
        new_header = []
        #
        if not self._header_cleanup:
            self._header_cleanup = {
                    u'datatype': u'data_type', 
                    u'scientific_name': u'scientific_name', 
                    u'scientific_authority': u'scientific_authority', 
                    u'sample_latitude_dd': u'latitude_dd', 
                    u'sample_longitude_dd': u'longitude_dd', 
                    u'sample_date': u'sampling_date', 
                    u'visit_year': u'sampling_year', 
                    u'visit_month': u'sampling_month', 
                    u'visit_day': u'sampling_day', 
                    u'sample_min_depth_m': u'sample_min_depth', 
                    u'sample_max_depth_m': u'sample_max_depth', 
                    u'sampler_type_code': u'sampler_type', 
                    u'variable.taxon_id': u'dyntaxa_id', 
                    u'dyntaxa_id': u'dyntaxa_id', 
                    u'taxon_kingdom': u'taxon_kingdom', 
                    u'taxon_phylum': u'taxon_phylum', 
                    u'taxon_class': u'taxon_class', 
                    u'taxon_order': u'taxon_order', 
                    u'taxon_family': u'taxon_family', 
                    u'taxon_genus': u'taxon_genus', 
                    u'taxon_species': u'taxon_species', 
                    u'orderer_code': u'orderer', 
                    u'reporting_institute_code': u'reporting_institute', 
                    u'sampling_laboratory_code': u'sampling_laboratory', 
                    u'analytical_laboratory_code': u'analytical_laboratory',   
                }            
        #
        for item in data_header:
            if item in self._header_cleanup:
                new_header.append(self._header_cleanup[item])                
            else:
                new_header.append(item)
        #
        return new_header



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
        self._update_obs_thread = threading.Thread(target = self.updateSpeciesObs, args=(log_row_id,))
        self._update_obs_thread.start()
        return None # No error message.
         
    def updateSpeciesObs(self, log_row_id):
        """ """
        #
        print(u'Species observations update. Started.')
        
        try:
            # Load resource file containing WoRMS info for taxa.
            worms_info_object = misc_utils.SpeciesWormsInfo()
            worms_info_object.loadSpeciesFromResource()
            
            # Mark all rows in db table before update starts.
            speciesobs_models.SpeciesObs.objects.all().update(last_update_date = u'0000-00-00')
    
            # Loop over all datasets.
            valid_datatypes = [
                               u'Epibenthos', 
                               u'GreySeal', 
                               u'HarbourSeal', 
                               u'Phytoplankton', 
                               u'RingedSeal',
                               u'Zoobenthos', 
                               u'Zooplankton', 
                               ###u'Speciesobs', 
                               ]
            #
            for dataset_queryset in datasets_models.Datasets.objects.all():
                
                if dataset_queryset.datatype in valid_datatypes: 
                    print(u'Loading data from: ' + dataset_queryset.ftp_file_path)
                else:
                    print(u'Skipped (wrong datatype): ' + dataset_queryset.ftp_file_path)
                    continue
                #

                admin_models.addResultLog(log_row_id, result_log = u'Extracting species obs from: ' + dataset_queryset.dataset_file_name + u'...')

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
                    try:
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
        #                     lat_dd = rowdict.get(u'sample_latitude_dd', u'').replace(u',', u'.')
        #                     long_dd = rowdict.get(u'sample_longitude_dd', u'').replace(u',', u'.')
                            lat_dd = rowdict.get(u'latitude_dd', u'').replace(u',', u'.')
                            long_dd = rowdict.get(u'longitude_dd', u'').replace(u',', u'.')
        #                     if self.isFloat(lat_dd) and self.isFloat(long_dd):
                            if True:
                                if (float(lat_dd) > 70.0) or (float(lat_dd) < 50.0) or (float(long_dd) > 25.0) or (float(long_dd) < 5.0):
                                    # Don't add to SpeciesObs if lat_dd/long_dd is outside the box.
                                    print(u'Row skipped, position outside box. Latitude: ' + lat_dd + u' Longitude: ' + long_dd + u' Row: ' + unicode(rowindex))
                                    continue
                            else:
                                # Don't add to SpeciesObs if lat_dd/long_dd is invalid.
                                continue
                            #
                            tmp_date = rowdict.get(u'sampling_date', u'')
                            tmp_year = u''
                            tmp_month = u''
                            tmp_day = u''
                            if len(tmp_date) >= 10:
                                tmp_year = tmp_date[0:4]
                                tmp_month = tmp_date[5:7]
                                tmp_day = tmp_date[8:10] 
                                
                            scientificname = rowdict.get(u'scientific_name', u'-') if rowdict.get(u'scientific_name') else u'-'
                            scientificauthority = rowdict.get(u'scientific_authority', u'-') if rowdict.get(u'scientific_authority') else u'-'
                            taxon_worms_info = worms_info_object.getTaxonInfoDict(scientificname)
                            if taxon_worms_info:
                                taxonkingdom = taxon_worms_info.get(u'kingdom', u'-') if taxon_worms_info.get(u'kingdom') else u'-'
                                taxonphylum = taxon_worms_info.get(u'phylum', u'-') if taxon_worms_info.get(u'phylum') else u'-'
                                taxonclass = taxon_worms_info.get(u'class', u'-') if taxon_worms_info.get(u'class') else u'-'
                                taxonorder = taxon_worms_info.get(u'order', u'-') if taxon_worms_info.get(u'order') else u'-'
                                taxonfamily = taxon_worms_info.get(u'family', u'-') if taxon_worms_info.get(u'family') else u'-'
                                taxongenus = taxon_worms_info.get(u'genus', u'-') if taxon_worms_info.get(u'genus') else u'-'
                            else:
                                taxonkingdom = u'-'
                                taxonphylum = u'-'
                                taxonclass = u'-'
                                taxonorder = u'-'
                                taxonfamily = u'-'
                                taxongenus = u'-'

                              
                            speciesobs = speciesobs_models.SpeciesObs(
                                data_type = rowdict.get(u'data_type', u''),
                                scientific_name = scientificname, 
                                scientific_authority = scientificauthority, 
        #                         latitude_dd = rowdict.get(u'sample_latitude_dd', u'').replace(u',', u'.'),
        #                         longitude_dd = rowdict.get(u'sample_longitude_dd', u'').replace(u',', u'.'),
                                latitude_dd = rowdict.get(u'latitude_dd', u'').replace(u',', u'.'),
                                longitude_dd = rowdict.get(u'longitude_dd', u'').replace(u',', u'.'),
                                sampling_date = rowdict.get(u'sampling_date', u''),
                                sampling_year = tmp_year,
                                sampling_month = tmp_month,
                                sampling_day = tmp_day,
                                sample_min_depth = rowdict.get(u'sample_min_depth', u''),
                                sample_max_depth = rowdict.get(u'sample_max_depth', u''),
                                sampler_type = rowdict.get(u'sampler_type', u''),
                                dyntaxa_id = rowdict.get(u'dyntaxa_id', u'') if rowdict.get(u'dyntaxa_id') else u'-',

#                                 taxon_kingdom = rowdict.get(u'taxon_kingdom', u'-') if rowdict.get(u'taxon_kingdom') else u'-',
#                                 taxon_phylum = rowdict.get(u'taxon_phylum', u'-') if rowdict.get(u'taxon_phylum') else u'-',
#                                 taxon_class = rowdict.get(u'taxon_class', u'-') if rowdict.get(u'taxon_class') else u'-',
#                                 taxon_order = rowdict.get(u'taxon_order', u'-') if rowdict.get(u'taxon_order') else u'-',
#                                 taxon_family = rowdict.get(u'taxon_family', u'-') if rowdict.get(u'taxon_family') else u'-',
#                                 taxon_genus = rowdict.get(u'taxon_genus', u'-') if rowdict.get(u'taxon_genus') else u'-',
#                                 taxon_species = rowdict.get(u'taxon_species', u'-') if rowdict.get(u'taxon_species') else u'-',

                                taxon_kingdom = taxonkingdom,
                                taxon_phylum = taxonphylum,
                                taxon_class = taxonclass,
                                taxon_order = taxonorder,
                                taxon_family = taxonfamily,
                                taxon_genus = taxongenus,
#                                 taxon_species = rowdict.get(u'species', u'-') if rowdict.get(u'species') else u'-',

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
                            
                    except Exception as e:
                        admin_models.addResultLog(log_row_id, result_log = u'- Error in row ' + unicode(rowindex) + u': ' + unicode(e))
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
            admin_models.changeLogRowStatus(log_row_id, status = u'FINISHED')
            #
            print(u'Species observations update. Finished.')    
        #
        except Exception as e:
            admin_models.addResultLog(log_row_id, result_log = u'- Failed. Error: ' + unicode(e))
            admin_models.changeLogRowStatus(log_row_id, status = u'FAILED')

    def isFloat(self, value):
        """ Useful utility. """
        try:
            float(value)
            return True
        except ValueError:
            return False     
    
#     def loadSpeciesObsInThread(self, log_row_id):
#         """ """
#         
#         return u"This feature is not implemented yet..."
#         
#         
#         # Check if update thread is running.
#         if self._update_obs_thread:
#             if self._update_obs_thread.is_alive():
#                 return u"Update is already running. Please try again later."
#         # Check if load thread is running.
#         if self._load_obs_thread:
#             if self._load_obs_thread.is_alive():
#                 return u"Load is already running. Please try again later."              
#         # Check if clean up thread is running.
#         if self._cleanup_obs_thread:
#             if self._cleanup_obs_thread.is_alive():
#                 return u"Clean up is already running. Please try again later."              
#         # Use a thread to relese the user. This task will take some time.
#         self._load_obs_thread = threading.Thread(target = self.loadSpeciesObs, args=(log_row_id,))
#         self._load_obs_thread.start()
#         return None # No error message.
#          
#     def loadSpeciesObs(self, log_row_id):
#         """ """
#         print(u'NOT IMPLEMENTED YET: SpeciesObsUtils.loadSpeciesObs()')
#         #
#         admin_models.changeLogRowStatus(log_row_id, status = u'FINISHED')
#         #
        
                  
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
        self._cleanup_obs_thread = threading.Thread(target = self.cleanUpSpeciesObs, args=(log_row_id,))
        self._cleanup_obs_thread.start()

        return None # No error message.
       
    def cleanUpSpeciesObs(self, log_row_id):
        """ """
#         # Remove deleted rows when there is no more need for them from the consumer side (SLU). 
#         speciesobs_models.SpeciesObs.objects.filter(status=u'DELETED').delete()

        # Deletes all rows.
        speciesobs_models.SpeciesObs.objects.all().delete()
        #
        admin_models.changeLogRowStatus(log_row_id, status = u'FINISHED')
        #
         
