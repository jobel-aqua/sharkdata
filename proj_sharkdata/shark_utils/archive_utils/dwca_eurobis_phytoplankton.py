#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2015 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

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
        self.individual_count_parameter = u'# counted'
        self.individual_count_unit = u'ind/analysed sample fraction'
        #
        self.sampling_effort_items = {u'SampledVolume(l)': u'sampled_volume_l'}
        self.sampling_protocol_items = {u'SamplerTypeCode': u'sampler_type_code', 
                                        u'MeshSize(um)': u'mesh_size_um', 
                                        u'MethodReference': u'method_reference_code'}        
        self.dynamic_properties_items = { }
        self.identification_qualifier_items = {u'SpeciesFlag': u'species_flag_code'}
        # Note: Moved to generated parameters in measurementorfact.
#         self.identification_qualifier_items = {u'SizeClass(HELCOM-PEG)': u'size_class',
#                                                u'SizeMin(um)': u'size_min_um',
#                                                u'SizeMax(um)': u'size_max_um',
#                                                u'SpeciesFlag': u'species_flag_code',
#                                                u'TrophicType': u'trophic_type',
#                                                u'CellVolume(um3)': u'reported_cell_volume_um3'}
        self.field_number_items = [u'sample_id', 
                                   u'sample_part_id'] 
        self.generated_parameters = {u'SizeClass(HELCOM-PEG)': u'size_class',
                                     u'SizeMin:um': u'size_min_um',
                                     u'SizeMax:um': u'size_max_um',
                                     u'TrophicType': u'trophic_type',
                                     u'CellVolume:um3': u'reported_cell_volume_um3'}
        #
        # Note: quality_flag is added to measurementRemarks in measurementorfact.
        #
        self.collection_code = u'SHARK Phytoplankton'
        
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
                u'id', 
                u'eventDate', 
                u'eventTime',
                u'year', 
                u'month', 
                u'day', 
                u'verbatimLocality', 
                u'decimalLatitude', 
                u'decimalLongitude',
                u'minimumDepthInMeters',
                u'maximumDepthInMeters',
                u'fieldNumber',
                u'scientificName', 
                u'identificationQualifier', 
                u'dynamicProperties', 
                u'sex', 
                u'lifeStage',
                u'individualCount', 
                u'scientificNameID', 
                u'kingdom', 
                u'phylum', 
                u'class', 
                u'order', 
                u'family', 
                u'genus', 
                u'scientificNameAuthorship', 
                u'samplingEffort',
                u'samplingProtocol', 
                u'fieldNotes', 
                u'eventRemarks', 
                u'occurrenceDetails', # For 'No species in sample', etc.
                u'ownerInstitutionCode', 
                u'recordedBy', 
                u'datasetName', 
                u'collectionCode', 
                u'country',
                u'countryCode',                 
            ]
        #
        return self.dwca_occurrence_columns

    def getDwcaMeasurementorfactColumns(self):
        """ """
        if not self.dwca_measurementorfact_columns:
            self.dwca_measurementorfact_columns = [
                u'id',
                u'occurrenceID', 
                u'measurementType', 
                u'measurementValue', 
                u'measurementUnit', 
                u'measurementDeterminedDate', 
                u'measurementDeterminedBy', 
                u'measurementMethod', 
                u'measurementRemarks', 
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
                u'station_name', 
                u'sample_date', 
                u'sample_time', 
                u'sample_latitude_dd', 
                u'sample_longitude_dd', 
                u'sampler_type_code', 
                u'sample_min_depth_m', 
                u'sample_max_depth_m',         
                u'sample_id', 
                u'sample_part_id', 
                #        
                u'scientific_name',
                u'size_class', 
                u'size_min_um', 
                u'size_max_um', 
                u'species_flag_code', 
                u'trophic_type', 
                u'reported_cell_volume_um3', 
            ]
        #
        return self.indata_occurrence_keys

    def getIndataMeasurementorfactKeyColumns(self):
        """ """
        if not self.indata_measurementorfact_key_columns:
            self.indata_measurementorfact_key_columns = [
                u'station_name', 
                u'sample_date', 
                u'sample_time', 
                u'sample_latitude_dd', 
                u'sample_longitude_dd', 
                u'sampler_type_code', 
                u'sample_min_depth_m', 
                u'sample_max_depth_m', 
                u'sample_id', 
                u'sample_part_id', 
                #        
                u'scientific_name',
                u'size_class', 
                u'size_min_um', 
                u'size_max_um', 
                u'species_flag_code', 
                u'trophic_type', 
                u'reported_cell_volume_um3', 
                # 
                u'parameter', 
                u'unit', 
            ]
        #
        return self.indata_measurementorfact_key_columns

    def getDwcaDefaultMapping(self):
        """ """
        if not self.dwca_default_mapping:
            self.dwca_default_mapping = {
#                 u'': u'datatype', 
                u'year': u'visit_year', 
#                 u'': u'project_code', 
                u'ownerInstitutionCode': u'orderer_code', 
                u'eventDate': u'sample_date', 
#                 u'': u'sample_latitude_dm', 
#                 u'': u'sample_longitude_dm', 
#                 u'': u'positioning_system_code', 
                u'verbatimLocality': u'station_name', 
#                 u'': u'platform_code', 
#                 u'': u'water_depth_m', 
                u'fieldNotes': u'visit_comment', 
#                 u'': u'wind_direction_code', 
#                 u'': u'wind_speed_ms', 
#                 u'': u'air_temperature_degc', 
#                 u'': u'air_pressure_hpa', 
#                 u'': u'weather_observation_code', 
#                 u'': u'cloud_observation_code', 
#                 u'': u'wave_observation_code', 
#                 u'': u'ice_observation_code', 
#                 u'': u'sea_status_code', 
#                 u'': u'wave_exposure_fetch', 
#                 u'': u'secchi_depth_m', 
#                 u'': u'secchi_depth_quality_flag', 
                u'minimumDepthInMeters': u'sample_min_depth_m', 
                u'maximumDepthInMeters': u'sample_max_depth_m', 
                u'recordedBy': u'sampling_laboratory_code', 
#                 u'': u'sampling_laboratory_accreditated', 
#                 u'': u'sampler_type_code', 
#                 u'': u'sampled_volume_l', 
#                 u'': u'preservation_method_code', 
                u'eventTime': u'sample_time', 
                u'decimalLatitude': u'sample_latitude_dd', 
                u'decimalLongitude': u'sample_longitude_dd', 
#                 u'': u'station_type_code', 
#                 u'': u'sample_id', 
#                 u'': u'sample_series', 
#                 u'': u'mesh_size_um', 
#                 u'': u'sample_part_id', 
                u'eventRemarks': u'sample_comment', 
                u'scientificName': u'scientific_name', 
#                 u'': u'reported_scientific_name', 
#                 u'': u'species_flag_code', 
#                 u'': u'trophic_type', 
#                 u'': u'parameter', 
#                 u'': u'value', 
#                 u'': u'unit', 
#                 u'': u'quality_flag', 
#                 u'': u'calc_by_dv', 
#                 u'': u'coefficient', 
#                 u'': u'size_class', 
#                 u'': u'size_class_ref_list_code', 
#                 u'': u'size_min_um', 
#                 u'': u'size_max_um', 
#                 u'': u'reported_cell_volume_um3', 
                u'measurementDeterminedBy': u'taxonomist', 
#                 u'': u'sedimentation_volume_ml', 
#                 u'': u'sedimentation_time_h', 
#                 u'': u'magnification', 
#                 u'': u'analytical_laboratory_code', 
#                 u'': u'analytical_laboratory_accreditated', 
                u'measurementDeterminedDate': u'analysis_date', 
                u'samplingProtocol': u'method_documentation', 
#                 u'': u'method_reference_code', 
#                 u'': u'counter_program', 
                u'measurementMethod': u'analysis_method_code', 
#                 u'': u'method_comment', 
#                 u'': u'plankton_sampling_method_code', 
                u'measurementRemarks': u'variable_comment', 
#                 u'': u'dyntaxa_id', 
#                 u'': u'expedition_id', 
#                 u'': u'monitoring_program_code', 
#                 u'': u'water_land_station_type_code', 
#                 u'': u'monitoring_purpose_code', 
#                 u'': u'station_viss_eu_id', 
#                 u'': u'reported_station_name', 
#                 u'': u'reporting_institute_code', 
#                 u'': u'reported_parameter', 
#                 u'': u'reported_value', 
#                 u'': u'reported_unit', 
#                 u'': u'data_holding_centre', 
#                 u'': u'internet_access', 
#                 u'': u'dataset_name', 
                u'datasetName': u'dataset_file_name', 
            }
        #
        return self.dwca_default_mapping

