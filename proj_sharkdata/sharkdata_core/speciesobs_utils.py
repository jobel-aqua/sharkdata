#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

# import os
import time
import threading
# from django.conf import settings
import app_speciesobs.models as speciesobs_models
import app_datasets.models as datasets_models
# import app_resources.models as resources_models
import sharkdata_core.resources_utils as resources_utils
import app_sharkdataadmin.models as admin_models
#
import sharkdata_core

@sharkdata_core.singleton
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
                    'occurrence_id',
                    #
                    'data_type', 
                    'scientific_name', 
                    'scientific_authority', 
                    'latitude_dd', 
                    'longitude_dd', 
                    'sampling_date', 
                    'sampling_year', 
                    'sampling_month', 
                    'sampling_day', 
                    'sample_min_depth', 
                    'sample_max_depth', 
                    'sampler_type', 
                    'dyntaxa_id', 
                    'taxon_kingdom', 
                    'taxon_phylum', 
                    'taxon_class', 
                    'taxon_order', 
                    'taxon_family', 
                    'taxon_genus', 
                    'taxon_species', 
                    'orderer', 
                    'reporting_institute', 
                    'sampling_laboratory', 
                    'analytical_laboratory',                     
                    'dataset_name',
                    'dataset_file_name',
                    #
                    'status', # Used by SLU.
#                     'last_update_date', # Used for internal purposes, may be external in the future.
#                     'last_status_change_date', # Not used now, but can be used in the future.

                    ]
        #
        return self._data_header

    def translateHeaders(self, data_header, 
                         resource_name = 'translate_speciesobs_headers', 
                         language = 'darwin_core'):
#                        language = 'english'):
        """ """
        return resources_utils.ResourcesUtils().translateHeaders(data_header, resource_name, language)
           
    def cleanUpHeader(self, data_header):
        """ Internal columns names from SHARKweb etc. are not stable yet. Replace old style with better style. """
        new_header = []
        #
        if not self._header_cleanup:
            self._header_cleanup = {
                    'datatype': 'data_type', 
                    'scientific_name': 'scientific_name', 
                    'scientific_authority': 'scientific_authority', 
                    'sample_latitude_dd': 'latitude_dd', 
                    'sample_longitude_dd': 'longitude_dd', 
                    'sample_date': 'sampling_date', 
                    'visit_year': 'sampling_year', 
                    'visit_month': 'sampling_month', 
                    'visit_day': 'sampling_day', 
                    'sample_min_depth_m': 'sample_min_depth', 
                    'sample_max_depth_m': 'sample_max_depth', 
                    'sampler_type_code': 'sampler_type', 
                    'variable.taxon_id': 'dyntaxa_id', 
                    'dyntaxa_id': 'dyntaxa_id', 
                    'taxon_kingdom': 'taxon_kingdom', 
                    'taxon_phylum': 'taxon_phylum', 
                    'taxon_class': 'taxon_class', 
                    'taxon_order': 'taxon_order', 
                    'taxon_family': 'taxon_family', 
                    'taxon_genus': 'taxon_genus', 
                    'taxon_species': 'taxon_species', 
                    'orderer_code': 'orderer', 
                    'reporting_institute_code': 'reporting_institute', 
                    'sampling_laboratory_code': 'sampling_laboratory', 
                    'analytical_laboratory_code': 'analytical_laboratory',   
                }            
        #
        for item in data_header:
            if item in self._header_cleanup:
                new_header.append(self._header_cleanup[item])                
            else:
                new_header.append(item)
        #
        return new_header



#     def updateSpeciesObsInThread(self, log_row_id):
#         """ """
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
#         self._update_obs_thread = threading.Thread(target = self.updateSpeciesObs, args=(log_row_id,))
#         self._update_obs_thread.start()
#         return None # No error message.
#          
    def updateSpeciesObs(self, log_row_id):
        """ """
        #
        print('Species observations update. Started.')
        
        try:
            # Load resource file containing WoRMS info for taxa.
            worms_info_object = sharkdata_core.SpeciesWormsInfo()
            worms_info_object.loadSpeciesFromResource()
            
            # Mark all rows in db table before update starts.
            speciesobs_models.SpeciesObs.objects.all().update(last_update_date = '0000-00-00')
    
            # Loop over all datasets.
            valid_datatypes = [
                               'Epibenthos', 
                               'GreySeal', 
                               'HarbourSeal', 
                               'Phytoplankton', 
                               'RingedSeal',
                               'Zoobenthos', 
                               'Zooplankton', 
                               ###'Speciesobs', 
                               ]
            #
            for dataset_queryset in datasets_models.Datasets.objects.all():
                
                if dataset_queryset.datatype in valid_datatypes: 
                    print('Loading data from: ' + dataset_queryset.ftp_file_path)
                else:
                    print('Skipped (wrong datatype): ' + dataset_queryset.ftp_file_path)
                    continue
                #

                admin_models.addResultLog(log_row_id, result_log = 'Extracting species obs from: ' + dataset_queryset.dataset_file_name + '...')

                #
                zipreader = sharkdata_core.SharkArchiveFileReader(dataset_queryset.ftp_file_path)
                try:
                    zipreader.open()
                    data = zipreader.getDataAsText()
                finally:
                    zipreader.close()                        
                #
                encoding = 'cp1252'
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
        #                     lat_dd = rowdict.get('sample_latitude_dd', '').replace(',', '.')
        #                     long_dd = rowdict.get('sample_longitude_dd', '').replace(',', '.')
                            lat_dd = rowdict.get('latitude_dd', '').replace(',', '.')
                            long_dd = rowdict.get('longitude_dd', '').replace(',', '.')
        #                     if self.isFloat(lat_dd) and self.isFloat(long_dd):
                            if True:
                                if (float(lat_dd) > 70.0) or (float(lat_dd) < 50.0) or (float(long_dd) > 25.0) or (float(long_dd) < 5.0):
                                    # Don't add to SpeciesObs if lat_dd/long_dd is outside the box.
                                    print('Row skipped, position outside box. Latitude: ' + lat_dd + ' Longitude: ' + long_dd + ' Row: ' + unicode(rowindex))
                                    continue
                            else:
                                # Don't add to SpeciesObs if lat_dd/long_dd is invalid.
                                continue
                            #
                            tmp_date = rowdict.get('sampling_date', '')
                            tmp_year = ''
                            tmp_month = ''
                            tmp_day = ''
                            if len(tmp_date) >= 10:
                                tmp_year = tmp_date[0:4]
                                tmp_month = tmp_date[5:7]
                                tmp_day = tmp_date[8:10] 
                                
                            scientificname = rowdict.get('scientific_name', '-') if rowdict.get('scientific_name') else '-'
                            scientificauthority = rowdict.get('scientific_authority', '-') if rowdict.get('scientific_authority') else '-'
                            taxon_worms_info = worms_info_object.getTaxonInfoDict(scientificname)
                            if taxon_worms_info:
                                taxonkingdom = taxon_worms_info.get('kingdom', '-') if taxon_worms_info.get('kingdom') else '-'
                                taxonphylum = taxon_worms_info.get('phylum', '-') if taxon_worms_info.get('phylum') else '-'
                                taxonclass = taxon_worms_info.get('class', '-') if taxon_worms_info.get('class') else '-'
                                taxonorder = taxon_worms_info.get('order', '-') if taxon_worms_info.get('order') else '-'
                                taxonfamily = taxon_worms_info.get('family', '-') if taxon_worms_info.get('family') else '-'
                                taxongenus = taxon_worms_info.get('genus', '-') if taxon_worms_info.get('genus') else '-'
                            else:
                                taxonkingdom = '-'
                                taxonphylum = '-'
                                taxonclass = '-'
                                taxonorder = '-'
                                taxonfamily = '-'
                                taxongenus = '-'

                              
                            speciesobs = speciesobs_models.SpeciesObs(
                                data_type = rowdict.get('data_type', ''),
                                scientific_name = scientificname, 
                                scientific_authority = scientificauthority, 
        #                         latitude_dd = rowdict.get('sample_latitude_dd', '').replace(',', '.'),
        #                         longitude_dd = rowdict.get('sample_longitude_dd', '').replace(',', '.'),
                                latitude_dd = rowdict.get('latitude_dd', '').replace(',', '.'),
                                longitude_dd = rowdict.get('longitude_dd', '').replace(',', '.'),
                                sampling_date = rowdict.get('sampling_date', ''),
                                sampling_year = tmp_year,
                                sampling_month = tmp_month,
                                sampling_day = tmp_day,
                                sample_min_depth = rowdict.get('sample_min_depth', ''),
                                sample_max_depth = rowdict.get('sample_max_depth', ''),
                                sampler_type = rowdict.get('sampler_type', ''),
                                dyntaxa_id = rowdict.get('dyntaxa_id', '') if rowdict.get('dyntaxa_id') else '-',

#                                 taxon_kingdom = rowdict.get('taxon_kingdom', '-') if rowdict.get('taxon_kingdom') else '-',
#                                 taxon_phylum = rowdict.get('taxon_phylum', '-') if rowdict.get('taxon_phylum') else '-',
#                                 taxon_class = rowdict.get('taxon_class', '-') if rowdict.get('taxon_class') else '-',
#                                 taxon_order = rowdict.get('taxon_order', '-') if rowdict.get('taxon_order') else '-',
#                                 taxon_family = rowdict.get('taxon_family', '-') if rowdict.get('taxon_family') else '-',
#                                 taxon_genus = rowdict.get('taxon_genus', '-') if rowdict.get('taxon_genus') else '-',
#                                 taxon_species = rowdict.get('taxon_species', '-') if rowdict.get('taxon_species') else '-',

                                taxon_kingdom = taxonkingdom,
                                taxon_phylum = taxonphylum,
                                taxon_class = taxonclass,
                                taxon_order = taxonorder,
                                taxon_family = taxonfamily,
                                taxon_genus = taxongenus,
#                                 taxon_species = rowdict.get('species', '-') if rowdict.get('species') else '-',

                                orderer = rowdict.get('orderer', '') if rowdict.get('orderer') else '-',
                                reporting_institute = rowdict.get('reporting_institute', '') if rowdict.get('reporting_institute') else '-',
                                sampling_laboratory = rowdict.get('sampling_laboratory', '') if rowdict.get('sampling_laboratory') else '-',
                                analytical_laboratory = rowdict.get('analytical_laboratory', '') if rowdict.get('analytical_laboratory') else '-',
                                #
                                occurrence_id = '', # Added below.
                                #
                                dataset_name = unicode(dataset_queryset.dataset_name),
                                dataset_file_name = unicode(dataset_queryset.dataset_file_name),
                 
#                                 ##### Example: 'POINT(-73.9869510 40.7560540)', Note: Order longitude - latitude.
#                                 geometry = 'POINT(' + rowdict.get('longitude_dd', '0.0').replace(',', '.') + ' ' + rowdict.get('latitude_dd', '0.0').replace(',', '.') + ')',
                 
                                )
                            
                            # Calculate DarwinCore Observation Id.
                            generated_occurrence_id = speciesobs.calculateDarwinCoreObservationIdAsMD5()
                            #
        #                     if speciesobs_models.SpeciesObs(
        #                         speciesobs.save()
                            #speciesobs_models.SpeciesObs.objects.filter(status='DELETED').delete()
                            try: 
                                obs_existing_row = speciesobs_models.SpeciesObs.objects.get(occurrence_id = generated_occurrence_id)
                            except:
                                obs_existing_row = None # Does not exist.
                            #
                            current_date = unicode(time.strftime('%Y-%m-%d'))
                            #
                            if obs_existing_row:
                                if obs_existing_row.status == 'ACTIVE':
                                    obs_existing_row.last_update_date = current_date
                                else:
                                    obs_existing_row.status= 'ACTIVE'
                                    obs_existing_row.last_update_date = current_date
                                    obs_existing_row.last_status_change_date = current_date
                                #    
                                obs_existing_row.save()
                            else:
                                speciesobs.occurrence_id = generated_occurrence_id
                                speciesobs.status = 'ACTIVE'
                                speciesobs.last_update_date = current_date
                                speciesobs.last_status_change_date = current_date
                                #
                                speciesobs.save()
                            
                    except Exception as e:
                        admin_models.addResultLog(log_row_id, result_log = '- Error in row ' + unicode(rowindex) + ': ' + unicode(e))
            #
            print('Species observations update. Mark not updated rows as DELETED.')
            #
            current_date = unicode(time.strftime('%Y-%m-%d'))
    #         speciesobs_models.SpeciesObs.objects.filter(last_update_date = '0000-00-00').update(status = 'DELETED')
    #         speciesobs_models.SpeciesObs.objects.filter(last_update_date = '0000-00-00').update(last_update_date = current_date)
            #
            datarows = speciesobs_models.SpeciesObs.objects.filter(last_update_date = '0000-00-00')
            for datarow in datarows:
                if datarow.status == 'DELETED':
                    datarow.last_update_date = current_date
                else:
                    datarow.status = 'DELETED'
                    datarow.last_update_date = current_date
                    datarow.last_status_change_date = current_date
                #
                datarow.save()
                
            #
            admin_models.changeLogRowStatus(log_row_id, status = 'FINISHED')
            #
            print('Species observations update. Finished.')    
        #
        except Exception as e:
            admin_models.addResultLog(log_row_id, result_log = '- Failed. Error: ' + unicode(e))
            admin_models.changeLogRowStatus(log_row_id, status = 'FAILED')

    def isFloat(self, value):
        """ Useful utility. """
        try:
            float(value)
            return True
        except ValueError:
            pass
        return False     
    
#     def cleanUpSpeciesObsInThread(self, log_row_id):
#         """ """
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
#         self._cleanup_obs_thread = threading.Thread(target = self.cleanUpSpeciesObs, args=(log_row_id,))
#         self._cleanup_obs_thread.start()
# 
#         return None # No error message.
       
    def cleanUpSpeciesObs(self, log_row_id):
        """ """
#         # Remove deleted rows when there is no more need for them from the consumer side (SLU). 
#         speciesobs_models.SpeciesObs.objects.filter(status='DELETED').delete()

        # Deletes all rows.
        speciesobs_models.SpeciesObs.objects.all().delete()
        #
        admin_models.changeLogRowStatus(log_row_id, status = 'FINISHED')
        #
         
