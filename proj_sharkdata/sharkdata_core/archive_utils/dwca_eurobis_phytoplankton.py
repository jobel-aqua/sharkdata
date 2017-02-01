#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import dwca_eurobis

class DwcaEurObisPhytoplankton(dwca_eurobis.DwcaEurObis):
    """ """

    def __init__(self):
        """ """
        #
        super(DwcaEurObisPhytoplankton, self).__init__()
        # 
#         self.param_unit_exclude_filter = {}
        #
        self.individual_count_parameter = '# counted'
        self.individual_count_unit = 'ind/analysed sample fraction'
        #
        self.sampling_effort_items = {'SampledVolume(l)': 'sampled_volume_l'}
        self.sampling_protocol_items = {'SamplerTypeCode': 'sampler_type_code', 
                                        'MeshSize(um)': 'mesh_size_um', 
                                        'MethodReference': 'method_reference_code'}        
        self.dynamic_properties_items = { }
        self.identification_qualifier_items = {'SpeciesFlag': 'species_flag_code'}
        # Note: Moved to generated parameters in measurementorfact.
#         self.identification_qualifier_items = {'SizeClass(HELCOM-PEG)': 'size_class',
#                                                'SizeMin(um)': 'size_min_um',
#                                                'SizeMax(um)': 'size_max_um',
#                                                'SpeciesFlag': 'species_flag_code',
#                                                'TrophicType': 'trophic_type',
#                                                'CellVolume(um3)': 'reported_cell_volume_um3'}
        self.field_number_items = ['sample_id', 
                                   'sample_part_id'] 
        self.generated_parameters = {'SizeClass(HELCOM-PEG)': 'size_class',
                                     'SizeMin:um': 'size_min_um',
                                     'SizeMax:um': 'size_max_um',
                                     'TrophicType': 'trophic_type',
                                     'CellVolume:um3': 'reported_cell_volume_um3'}
        #
        # Note: quality_flag is added to measurementRemarks in measurementorfact.
        #
        self.collection_code = 'SHARK Phytoplankton'
        
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
                'size_class', 
                'size_min_um', 
                'size_max_um', 
                'species_flag_code', 
                'trophic_type', 
                'reported_cell_volume_um3', 
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
                'size_class', 
                'size_min_um', 
                'size_max_um', 
                'species_flag_code', 
                'trophic_type', 
                'reported_cell_volume_um3', 
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
#                 '': 'sample_latitude_dm', 
#                 '': 'sample_longitude_dm', 
#                 '': 'positioning_system_code', 
                'verbatimLocality': 'station_name', 
#                 '': 'platform_code', 
#                 '': 'water_depth_m', 
                'fieldNotes': 'visit_comment', 
#                 '': 'wind_direction_code', 
#                 '': 'wind_speed_ms', 
#                 '': 'air_temperature_degc', 
#                 '': 'air_pressure_hpa', 
#                 '': 'weather_observation_code', 
#                 '': 'cloud_observation_code', 
#                 '': 'wave_observation_code', 
#                 '': 'ice_observation_code', 
#                 '': 'sea_status_code', 
#                 '': 'wave_exposure_fetch', 
#                 '': 'secchi_depth_m', 
#                 '': 'secchi_depth_quality_flag', 
                'minimumDepthInMeters': 'sample_min_depth_m', 
                'maximumDepthInMeters': 'sample_max_depth_m', 
                'recordedBy': 'sampling_laboratory_code', 
#                 '': 'sampling_laboratory_accreditated', 
#                 '': 'sampler_type_code', 
#                 '': 'sampled_volume_l', 
#                 '': 'preservation_method_code', 
                'eventTime': 'sample_time', 
                'decimalLatitude': 'sample_latitude_dd', 
                'decimalLongitude': 'sample_longitude_dd', 
#                 '': 'station_type_code', 
#                 '': 'sample_id', 
#                 '': 'sample_series', 
#                 '': 'mesh_size_um', 
#                 '': 'sample_part_id', 
                'eventRemarks': 'sample_comment', 
                'scientificName': 'scientific_name', 
#                 '': 'reported_scientific_name', 
#                 '': 'species_flag_code', 
#                 '': 'trophic_type', 
#                 '': 'parameter', 
#                 '': 'value', 
#                 '': 'unit', 
#                 '': 'quality_flag', 
#                 '': 'calc_by_dv', 
#                 '': 'coefficient', 
#                 '': 'size_class', 
#                 '': 'size_class_ref_list_code', 
#                 '': 'size_min_um', 
#                 '': 'size_max_um', 
#                 '': 'reported_cell_volume_um3', 
                'measurementDeterminedBy': 'taxonomist', 
#                 '': 'sedimentation_volume_ml', 
#                 '': 'sedimentation_time_h', 
#                 '': 'magnification', 
#                 '': 'analytical_laboratory_code', 
#                 '': 'analytical_laboratory_accreditated', 
                'measurementDeterminedDate': 'analysis_date', 
                'samplingProtocol': 'method_documentation', 
#                 '': 'method_reference_code', 
#                 '': 'counter_program', 
                'measurementMethod': 'analysis_method_code', 
#                 '': 'method_comment', 
#                 '': 'plankton_sampling_method_code', 
                'measurementRemarks': 'variable_comment', 
#                 '': 'dyntaxa_id', 
#                 '': 'expedition_id', 
#                 '': 'monitoring_program_code', 
#                 '': 'water_land_station_type_code', 
#                 '': 'monitoring_purpose_code', 
#                 '': 'station_viss_eu_id', 
#                 '': 'reported_station_name', 
#                 '': 'reporting_institute_code', 
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

