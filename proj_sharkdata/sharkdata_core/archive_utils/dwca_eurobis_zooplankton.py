#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import dwca_eurobis

class DwcaEurObisZooplankton(dwca_eurobis.DwcaEurObis):
    """ """

    def __init__(self):
        """ """
        #
        super(DwcaEurObisZooplankton, self).__init__()
        # 
#         self.param_unit_exclude_filter = {}
        #
        self.individual_count_parameter = '# counted'
        self.individual_count_unit = 'ind/analysed sample fraction'
        #
        self.sampling_effort_items = {'SampledVolume(l)': 'sampled_volume_l', 
                                      'SamplerArea(cm2)': 'sampler_area_cm2', 
                                      'WireAngle(deg)': 'wire_angle_deg', 
                                      'SampleSplittingCode': 'sample_splitting_code'}
        self.sampling_protocol_items = {'SamplerTypeCode': 'sampler_type_code', 
                                        'MeshSize(um)': 'mesh_size_um', 
                                        'MethodReference': 'method_reference_code'}        
        self.dynamic_properties_items = { }
        self.identification_qualifier_items = {'SizeClass': 'size_class',
                                               'SizeMin(um)': 'size_min_um',
                                               'SizeMax(um)': 'size_max_um',
                                               'SpeciesFlag': 'species_flag_code'}
        self.field_number_items = ['sample_id', 
                                   'sample_part_id'] 
        self.generated_parameters = {}
        #
        # Note: quality_flag is added to measurementRemarks in measurementorfact.
        #
        self.collection_code = 'SHARK Zooplankton'
        
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
                'sample_min_depth_m', 
                'sample_max_depth_m',         
                'sample_id', 
                'sample_part_id', 
                #        
                'scientific_name',
                'species_flag_code', 
                'size_class', 
                'dev_stage_code', 
                'sex_code', 
                'size_min_um', 
                'size_max_um', 
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
                'sample_min_depth_m', 
                'sample_max_depth_m', 
                'sample_id', 
                'sample_part_id', 
                #        
                'scientific_name',
                'species_flag_code', 
                'size_class', 
                'dev_stage_code', 
                'sex_code', 
                'size_min_um', 
                'size_max_um', 
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
                'verbatimLocality': 'station_name', 
#                 '': 'platform_code', 
#                 '': 'expedition_id', 
#                 '': 'sample_latitude_dm', 
#                 '': 'sample_longitude_dm', 
#                 '': 'positioning_system_code', 
#                 '': 'water_depth_m', 
#                 '': 'visit_id', 
                'fieldNotes': 'visit_comment', 
#                 '': 'wind_direction_code', 
#                 '': 'wind_speed_ms', 
#                 '': 'air_temperature_degc', 
#                 '': 'air_pressure_hpa', 
#                 '': 'weather_observation_code', 
#                 '': 'cloud_observation_code', 
#                 '': 'wave_observation_code', 
#                 '': 'ice_observation_code', 
#                 '': 'secchi_depth_m', 
#                 '': 'secchi_depth_quality_flag', 
#                 '': 'sea_status_code', 
#                 '': 'sample_id', 
                'minimumDepthInMeters': 'sample_min_depth_m', 
                'maximumDepthInMeters': 'sample_max_depth_m', 
                'recordedBy': 'sampling_laboratory_code', 
#                 '': 'sampling_laboratory_accreditated', 
#                 '': 'sampler_type_code', 
#                 '': 'sampler_area_cm2', 
#                 '': 'sampled_volume_l', 
#                 '': 'calculation_method', 
#                 '': 'mesh_size_um', 
#                 '': 'wire_angle_deg', 
#                 '': 'preservation_method_code', 
                'eventTime': 'sample_time', 
#                 '': 'sample_series', 
#                 '': 'sample_part_id', 
                'eventRemarks': 'sample_comment', 
#                 '': 'sample_splitting_code', 
#                 '': 'number_of_portions', 
#                 '': 'counted_portions', 
#                 '': 'magnification', 
                'scientificName': 'scientific_name', 
#                 '': 'reported_scientific_name', 
#                 '': 'species_flag_code', 
#                 '': 'parameter', 
#                 '': 'value', 
#                 '': 'unit', 
#                 '': 'quality_flag', 
#                 '': 'calc_by_dv', 
                'sex': 'sex_code', 
#                 '': 'size_class', 
#                 '': 'size_min_um', 
#                 '': 'size_max_um', 
                'lifeStage': 'dev_stage_code', 
#                 '': 'taxonomist', 
#                 '': 'analytical_laboratory_code', 
#                 '': 'analytical_laboratory_accreditated', 
                'measurementDeterminedDate': 'analysis_date', 
#                 '': 'method_documentation', 
                'samplingProtocol': 'method_reference_code', 
                'measurementMethod': 'plankton_sampling_method_code', 
                'measurementDeterminedBy': 'analysed_by', 
                'measurementRemarks': 'variable_comment', 
#                 '': 'dyntaxa_id', 
#                 '': 'station_viss_eu_id', 
                'decimalLatitude': 'sample_latitude_dd', 
                'decimalLongitude': 'sample_longitude_dd', 
#                 '': 'monitoring_program_code', 
#                 '': 'water_land_station_type_code', 
#                 '': 'station_type_code', 
#                 '': 'monitoring_purpose_code', 
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

