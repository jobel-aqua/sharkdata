#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2015 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# import dwca_base
# 
# class DwcaEurObis(dwca_base.DwcaBase):
#     """ """
# 
#     def __init__(self):
#         """ """
#         #
#         super(DwcaEurObis, self).__init__()
#         #
#         self.xml_templates_path = u'dwca_xml_templates'
#         self.meta_file_name = u'meta_eurobis.xml'
#         self.eml_file_name = u'eml_eurobis.xml'
#         self.scientific_name_id_urn = u'urn:lsid:marinespecies.org:taxname:'
#         #
#         self.clear()
#                 
#     def createArchivePartOccurrence(self, row_dict, 
#                                     event_key_string, 
#                                     occurrence_key_string, 
#                                     measurementorfact_key_string, 
#                                     occurrence_key_list):
#         """ Concrete method. """
#         # Don't add parameters with no species. TODO: Maybe later as extra info on each row.
#         if not row_dict.get(u'scientific_name', None):
#             return
#         
#         if occurrence_key_string and (occurrence_key_string not in occurrence_key_list):
#             #
#             occurrence_key_list.append(occurrence_key_string)
#             #
#             occurrence_dict = {}
#             # Direct field mapping.
#             for column_name in self.getDwcaOccurrenceColumns():
#                 if column_name in self.getDwcaDefaultMapping():
#                     occurrence_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], u'')
#             # Add more.
#             occurrence_dict[u'id'] = occurrence_key_string
#             #
#             occurrence_dict[u'year'] = row_dict[u'sample_date'][0:4]
#             occurrence_dict[u'month'] = row_dict[u'sample_date'][5:7]
#             occurrence_dict[u'day'] = row_dict[u'sample_date'][8:10] 
#             occurrence_dict[u'country'] = u'Sweden'
#             occurrence_dict[u'countryCode'] = u'SE'                
#             #
#             # Sampling effort.        
#             if len(self.sampling_effort_items) > 0:
#                 sampling_effort_list = []
#                 for key, value in self.sampling_effort_items.items():
#                     if row_dict.get(value, None):
#                         sampling_effort_list.append(key + u'=' + row_dict.get(value, u''))
#                 occurrence_dict[u'samplingEffort'] = u'; '.join(sampling_effort_list)
#             # Sampling protocol.        
#             if len(self.sampling_protocol_items) > 0:
#                 sampling_protocol_list = []
#                 for key, value in self.sampling_protocol_items.items():
#                     if row_dict.get(value, None):
#                         sampling_protocol_list.append(key + u'=' + row_dict.get(value, u''))
#                 occurrence_dict[u'samplingProtocol'] = u'; '.join(sampling_protocol_list)
#                  
# #             sampling_protocol_list = []
# #             if row_dict.get(u'samplingProtocol', None):
# #                 sampling_protocol_list.append(u'MethodReference=' + row_dict.get(u'samplingProtocol', u''))
# #             if row_dict.get(u'sampler_type_code', None):
# #                 sampling_protocol_list.append(u'SamplerType=' + row_dict.get(u'sampler_type_code', u''))
# #             occurrence_dict[u'samplingProtocol'] = u'; '.join(sampling_protocol_list)
#             #
#             # Add WoRMS data.
#             if self.worms_info_object:
#                 taxon_worms_info = self.worms_info_object.getTaxonInfoDict(row_dict[u'scientific_name'])
#                 if taxon_worms_info:
#                     if taxon_worms_info[u'aphia_id']:
#                         occurrence_dict[u'scientificNameID'] = self.scientific_name_id_urn + taxon_worms_info[u'aphia_id']
#                     occurrence_dict[u'kingdom'] = taxon_worms_info[u'kingdom']
#                     occurrence_dict[u'phylum'] = taxon_worms_info[u'phylum']
#                     occurrence_dict[u'class'] = taxon_worms_info[u'class']
#                     occurrence_dict[u'order'] = taxon_worms_info[u'order']
#                     occurrence_dict[u'family'] = taxon_worms_info[u'family']
#                     occurrence_dict[u'genus'] = taxon_worms_info[u'genus']
#                     occurrence_dict[u'specificEpithet'] = u'' # TODO:
#                     occurrence_dict[u'scientificNameAuthorship'] = taxon_worms_info[u'authority']
#             #
#             occurrence_dict[u'collectionCode'] = self.collection_code
#             occurrence_dict[u'country'] = u'Sweden'
#             occurrence_dict[u'countryCode'] = u'SE'
#             #
#             self.dwca_occurrence.append(occurrence_dict)
#             self.dwca_occurrence_lookup[occurrence_key_string] = occurrence_dict
# 
#         # Add 'individualCount' and 'sampling effort' info.
#         if self.individual_count_parameter: 
#             if (row_dict[u'parameter'] == self.individual_count_parameter) and (row_dict[u'unit'] == self.individual_count_unit):
# #                 for searchrow_dict in self.dwca_occurrence:
# #                     if searchrow_dict[u'id'] == occurrence_key_string:
# #                         searchrow_dict[u'individualCount'] = row_dict.get(u'value', u'')
# #                         break # Exit for-loop.
#                 self.dwca_occurrence_lookup[occurrence_key_string][u'individualCount'] = row_dict.get(u'value', u'')
#             
#             
#     def createArchivePartMeasurementorfact(self, row_dict, 
#                                            event_key_string, 
#                                            occurrence_key_string, 
#                                            measurementorfact_key_string, 
#                                            measurementorfact_key_list):
#         """ Concrete method. """
#         # Don't add parameters with no species. TODO: Maybe later as extra info on each row.
#         if not row_dict.get(u'scientific_name', None):
#             return
# 
#         if measurementorfact_key_string and (measurementorfact_key_string not in measurementorfact_key_list):
#             # One in occurrence.txt, the rest in measurementorfact.txt. Skip "# counted".
#             if self.individual_count_parameter:
#                 if (row_dict[u'parameter'] == self.individual_count_parameter) and (row_dict[u'unit'] == self.individual_count_unit):
#                     return # This one should only be used in the occurrence table.
#             #
#             measurementorfact_key_list.append(measurementorfact_key_string)
#             #
#             measurementorfact_dict = {}
#             # Direct field mapping.
#             for column_name in self.getDwcaMeasurementorfactColumns():
#                 if column_name in self.getDwcaDefaultMapping():
#                     measurementorfact_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], u'')
#             # Add more.
#             measurementorfact_dict[u'id'] = self.measurementorfact_seq_no
#             self.measurementorfact_seq_no += 1
#             measurementorfact_dict[u'occurrenceID'] = occurrence_key_string
#             #
#             measurementorfact_dict[u'measurementType'] = row_dict[u'parameter']
#             measurementorfact_dict[u'measurementValue'] = row_dict[u'value']
#             measurementorfact_dict[u'measurementUnit'] = row_dict[u'unit']
#             
# #             # TODO: Remove this later. ERROR in Bacterioplankton data.
# #             if row_dict[u'unit'] == u'fgCcell': measurementorfact_dict[u'measurementType'] = u'fg C/cell'
# #             if row_dict[u'unit'] == u'µm3cell': measurementorfact_dict[u'measurementUnit'] = u'µm3/cell'
# #             if row_dict[u'unit'] == u'cellsl': measurementorfact_dict[u'measurementUnit'] = u'cells/l'
# #             if row_dict[u'unit'] == u'cellsld': measurementorfact_dict[u'measurementUnit'] = u'cells/l/d'
# 
#             # Zooplankton. EurOBIS don't like the same parameter name for ind/m2 and ind/m3. 
#             if (row_dict[u'parameter'] == u'Abundance') and (row_dict[u'unit'] == u'ind/m2'): 
#                 measurementorfact_dict[u'measurementType'] = u'Abundance/area'
#             if (row_dict[u'parameter'] == u'Abundance') and (row_dict[u'unit'] == u'ind/m3'): 
#                 measurementorfact_dict[u'measurementType'] = u'Abundance/volume'
#             #
#             self.dwca_measurementorfact.append(measurementorfact_dict)
#         #
#         else:
#             pass
#             # TODO: For development only. Remove in production. 
#             if row_dict[u'unit'] == u'ind/m3':
#                 pass # Too much...
#             else:
#                 if measurementorfact_key_string:
#                     print(u'DEBUG: Duplicate key in measurementorfact: ' + measurementorfact_key_string)
# 
# 
# 
# # class DarwinCoreArchiveFormatForSampleData(DarwinCoreArchiveFormat):
# #     """ """
# # 
# #     def __init__(self, datatype, settings_file_name = None, settings_dir_path = None,
# #                  meta_file_name = u'', eml_file_name = u'',
# #                  worms_info_object = None):
# #         """ """
# #         self.clear() 
# #         super(DarwinCoreArchiveFormatForSampleData, self).__init__(datatype, 
# #                                                       settings_file_name, 
# #                                                       settings_dir_path,
# #                                                       meta_file_name ,
# #                                                       eml_file_name,
# #                                                       worms_info_object)
# #     
# #     def createArchiveParts(self, dataset):
# #         """ """
# #         self.clear()
# #         direct_map = self.settings[u'direct_mapping']
# #         # List of used key strings to avoid duplicates.
# #         event_key_list = []
# #         occurrence_key_list = []
# #         measurementorfact_key_list = []
# #         # Sequence numbers for id columns.
# #         event_seq_no = 0
# #         occurrence_seq_no = 0
# #         measurementorfact_seq_no = 0
# #         # Get header and iterate over rows in the dataset.
# #         header = dataset.data_header
# #         for row in dataset.data_rows:
# #             # Connect header and row content to a dictionary for easy access.
# #             row_dict = dict(zip(header, row))
# #             # Create key strings.
# #             event_key_string = self.createKeyString(row_dict, self.settings[u'indata_event_keys']) 
# #             occurrence_key_string = self.createKeyString(row_dict, self.settings[u'indata_occurrence_keys']) 
# #             measurementorfact_key_string = self.createKeyString(row_dict, self.settings[u'indata_measurementorfact_keys'])             
# #             # Darwin Core: Event.
# #             if event_key_string and (event_key_string not in event_key_list):
# #                 event_key_list.append(event_key_string)
# #                 #
# #                 event_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings[u'event_columns']:
# #                     if column_name in direct_map:
# #                         event_dict[column_name] = row_dict.get(direct_map[column_name], u'')
# #                 # Add more.
# #                 event_dict[u'id'] = event_seq_no
# #                 event_seq_no += 1
# #                 event_dict[u'eventID'] = event_key_string
# #                 event_dict[u'samplingProtocol'] = u'Protocol for ' + row_dict[u'datatype'] # ???
# #                 event_dict[u'type'] = u'Sampling event' # ???
# #     
# #                 event_dict[u'month'] = row_dict[u'visit_date'][5:7]
# #                 event_dict[u'month'] = row_dict[u'visit_date'][5:7]
# #                 event_dict[u'day'] = row_dict[u'visit_date'][8:10] 
# #                 event_dict[u'country'] = u'Sweden'
# #                 event_dict[u'countryCode'] = u'SE'                
# #                 #
# #                 self.dwca_event.append(event_dict) 
# #                 
# #             # Darwin Core: Occurrence.
# #             if occurrence_key_string and (occurrence_key_string not in occurrence_key_list):
# #                 occurrence_key_list.append(occurrence_key_string)
# #                 #
# #                 occurrence_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings[u'occurrence_columns']:
# #                     if column_name in direct_map:
# #                         occurrence_dict[column_name] = row_dict.get(direct_map[column_name], u'')
# #                 # Add more.
# #                 occurrence_dict[u'id'] = occurrence_seq_no
# #                 occurrence_seq_no += 1
# #                 occurrence_dict[u'eventID'] = event_key_string
# #                 occurrence_dict[u'occurrenceID'] = occurrence_key_string
# # 
# #                 occurrence_dict[u'quantity'] = row_dict[u'value']
# #                 if row_dict[u'unit']:
# #                     occurrence_dict[u'quantityType'] = row_dict[u'parameter'] + u' (' + row_dict[u'unit'] + u')'
# #                 else:
# #                     occurrence_dict[u'quantityType'] = row_dict[u'parameter']
# #                 occurrence_dict[u'country'] = u'Sweden'
# #                 occurrence_dict[u'countryCode'] = u'SE'                
# #                 #
# #                 self.dwca_occurrence.append(occurrence_dict) 
# #                 
# #             # Darwin Core: Measurementorfact.
# #             if measurementorfact_key_string and (measurementorfact_key_string not in measurementorfact_key_list):
# #                 measurementorfact_key_list.append(measurementorfact_key_string)
# #                 #
# #                 measurementorfact_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings[u'measurementorfact_columns']:
# #                     if column_name in direct_map:
# #                         measurementorfact_dict[column_name] = row_dict.get(direct_map[column_name], u'')
# #                 # Add more.
# #                 measurementorfact_dict[u'id'] = measurementorfact_seq_no
# #                 measurementorfact_seq_no += 1
# #                 #    
# #                 self.dwca_measurementorfact.append(measurementorfact_dict) 
