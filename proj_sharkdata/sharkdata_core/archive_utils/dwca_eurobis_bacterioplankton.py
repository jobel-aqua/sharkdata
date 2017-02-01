#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import dwca_eurobis

class DwcaEurObisBacterioplankton(dwca_eurobis.DwcaEurObis):
    """ """

    def __init__(self):
        """ """
        #
        super(DwcaEurObisBacterioplankton, self).__init__()
        # 
#         self.param_unit_exclude_filter = {}
        #
        self.individual_count_parameter = None
        self.individual_count_unit = None
        #
        self.sampling_effort_items = {'SampledVolume(l)': 'sampled_volume_l', 
                                      'AnalysedVolume(cm3)': 'analysed_volume_cm3'}
        self.sampling_protocol_items = {'SamplerTypeCode': 'sampler_type_code', 
                                        'MethodReference': 'method_reference_code'}        
        self.dynamic_properties_items = {}
        self.identification_qualifier_items = {}
        self.field_number_items = ['sample_series', 
                                   'sample_id', 
                                   'sample_part_id'] 
        self.generated_parameters = {}
        #
        # Note: quality_flag is added to measurementRemarks in measurementorfact.
        #
        self.collection_code = 'SHARK Bacterioplankton'
        
#     def getDwcaEventColumns(self):
#         """ """
#         if not self.dwca_event_columns:
#             self.dwca_event_columns = []
#         #
#         return self.dwca_event_columns

    def getDwcaOccurrenceColumns(self):
        """ """
        if not self.dwca_occurrence_columns:
            self.dwca_occurrence_columns = [
                'id', 
                'eventDate', 
                'eventTime',
                'year', 
                'month', 
                'day', 
                'verbatimLocality', 
                'decimalLatitude', 
                'decimalLongitude',
                'minimumDepthInMeters',
                'maximumDepthInMeters',
                'fieldNumber',
                'scientificName', 
                'identificationQualifier', 
                'dynamicProperties', 
                'sex', 
                'lifeStage',
                'individualCount', 
                'scientificNameID', 
                'kingdom', 
                'phylum', 
                'class', 
                'order', 
                'family', 
                'genus', 
                'scientificNameAuthorship', 
                'samplingEffort',
                'samplingProtocol', 
                'fieldNotes', 
                'eventRemarks', 
                'occurrenceDetails', # For 'No species in sample', etc.
                'ownerInstitutionCode', 
                'recordedBy', 
                'datasetName', 
                'collectionCode', 
                'country',
                'countryCode',                 
            ]
        #
        return self.dwca_occurrence_columns

    def getDwcaMeasurementorfactColumns(self):
        """ """
        if not self.dwca_measurementorfact_columns:
            self.dwca_measurementorfact_columns = [
                'id',
                'occurrenceID', 
                'measurementType', 
                'measurementValue', 
                'measurementUnit', 
                'measurementDeterminedDate', 
                'measurementDeterminedBy', 
                'measurementMethod', 
                'measurementRemarks', 
            ]
        #
        return self.dwca_measurementorfact_columns

#     def getIndataEventKeyColumns(self):
#         """ """
#         if not self.indata_event_key_columns:
#             self.indata_event_key_columns = []
#         #
#         return self.indata_event_key_columns

    def getIndataOccurrenceKeyColumns(self):
        """ """
        if not self.indata_occurrence_keys:
            self.indata_occurrence_keys = [
                'station_name', 
                'sample_date', 
                'sample_time', 
                'sample_latitude_dd', 
                'sample_longitude_dd', 
                'sampler_type_code', 
                'sample_depth_m', 
                'sample_min_depth_m', 
                'sample_max_depth_m', 
                'sample_series', 
                'sample_id', 
                'sample_part_id', 
                #        
                'scientific_name', 
            ]
        #
        return self.indata_occurrence_keys

    def getIndataMeasurementorfactKeyColumns(self):
        """ """
        if not self.indata_measurementorfact_key_columns:
            self.indata_measurementorfact_key_columns = [
                'station_name', 
                'sample_date', 
                'sample_time', 
                'sample_latitude_dd', 
                'sample_longitude_dd', 
                'sampler_type_code', 
                'sample_depth_m', 
                'sample_min_depth_m', 
                'sample_max_depth_m',         
                'sample_series', 
                'sample_id', 
                'sample_part_id', 
                #
                'scientific_name',
                # 
                'parameter', 
                'unit', 
            ]
        #
        return self.indata_measurementorfact_key_columns

    def getDwcaDefaultMapping(self):
        """ """
        if not self.dwca_default_mapping:
            self.dwca_default_mapping = {
#                 '': 'datatype', 
                'year': 'visit_year', 
#                 '': 'project_code', 
                'ownerInstitutionCode': 'orderer_code', 
                'eventDate': 'sample_date', 
                'eventTime': 'sample_time', 
#                 '': 'platform_code', 
                'verbatimLocality': 'station_name', 
#                 '': 'sample_latitude_dm', 
#                 '': 'sample_longitude_dm', 
#                 '': 'positioning_system_code', 
#                 '': 'water_depth_m', 
                'fieldNotes': 'visit_comment', 
#                 '': 'sample_id', 
#                 '': 'sample_part_id', 
                'minimumDepthInMeters': 'sample_min_depth_m', 
                'maximumDepthInMeters': 'sample_max_depth_m', 
                'recordedBy': 'sampling_laboratory_code', 
#                 '': 'sampling_laboratory_accreditated', 
#                 '': 'sampler_type_code', 
#                 '': 'sampled_volume_l', 
                'eventRemarks': 'sample_comment', 
                'scientificName': 'scientific_name', 
#                 '': 'parameter', 
#                 '': 'value', 
#                 '': 'unit', 
#                 '': 'quality_flag', 
#                 '': 'calc_by_dv', 
#                 '': 'analytical_laboratory_code', 
#                 '': 'analytical_laboratory_accreditated', 
                'measurementDeterminedDate': 'analysis_date', 
                'measurementDeterminedBy': 'analysed_by', 
#                 '': 'analysed_volume_cm3', 
#                 '': 'coefficient', 
#                 '': 'counted_portions', 
                'measurementMethod': 'analysis_method_code', 
#                 '': 'method_documentation', 
                'samplingProtocol': 'method_reference_code', 
                'measurementRemarks': 'variable_comment', 
#                 '': 'preservation_method_code', 
#                 '': 'sample_series', 
#                 '': 'station_viss_eu_id', 
#                 '': 'visit_id', 
                'decimalLatitude': 'sample_latitude_dd', 
                'decimalLongitude': 'sample_longitude_dd', 
#                 '': 'monitoring_program_code', 
#                 '': 'water_land_station_type_code', 
#                 '': 'reporting_institute_code', 
#                 '': 'reported_station_name', 
#                 '': 'reported_parameter', 
#                 '': 'reported_value', 
#                 '': 'reported_unit', 
#                 '': 'data_holding_centre', 
#                 '': 'internet_access', 
#                 '': 'dataset_name', 
                'datasetName': 'dataset_file_name', 
            }
        #
        return self.dwca_default_mapping

