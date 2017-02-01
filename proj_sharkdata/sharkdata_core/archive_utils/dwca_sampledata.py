#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

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
#         self.xml_templates_path = 'dwca_xml_templates'
#         self.meta_file_name = 'meta_eurobis.xml'
#         self.eml_file_name = 'eml_eurobis.xml'
#         self.scientific_name_id_urn = 'urn:lsid:marinespecies.org:taxname:'
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
#         if not row_dict.get('scientific_name', None):
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
#                     occurrence_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], '')
#             # Add more.
#             occurrence_dict['id'] = occurrence_key_string
#             #
#             occurrence_dict['year'] = row_dict['sample_date'][0:4]
#             occurrence_dict['month'] = row_dict['sample_date'][5:7]
#             occurrence_dict['day'] = row_dict['sample_date'][8:10] 
#             occurrence_dict['country'] = 'Sweden'
#             occurrence_dict['countryCode'] = 'SE'                
#             #
#             # Sampling effort.        
#             if len(self.sampling_effort_items) > 0:
#                 sampling_effort_list = []
#                 for key, value in self.sampling_effort_items.items():
#                     if row_dict.get(value, None):
#                         sampling_effort_list.append(key + '=' + row_dict.get(value, ''))
#                 occurrence_dict['samplingEffort'] = '; '.join(sampling_effort_list)
#             # Sampling protocol.        
#             if len(self.sampling_protocol_items) > 0:
#                 sampling_protocol_list = []
#                 for key, value in self.sampling_protocol_items.items():
#                     if row_dict.get(value, None):
#                         sampling_protocol_list.append(key + '=' + row_dict.get(value, ''))
#                 occurrence_dict['samplingProtocol'] = '; '.join(sampling_protocol_list)
#                  
# #             sampling_protocol_list = []
# #             if row_dict.get('samplingProtocol', None):
# #                 sampling_protocol_list.append('MethodReference=' + row_dict.get('samplingProtocol', ''))
# #             if row_dict.get('sampler_type_code', None):
# #                 sampling_protocol_list.append('SamplerType=' + row_dict.get('sampler_type_code', ''))
# #             occurrence_dict['samplingProtocol'] = '; '.join(sampling_protocol_list)
#             #
#             # Add WoRMS data.
#             if self.worms_info_object:
#                 taxon_worms_info = self.worms_info_object.getTaxonInfoDict(row_dict['scientific_name'])
#                 if taxon_worms_info:
#                     if taxon_worms_info['aphia_id']:
#                         occurrence_dict['scientificNameID'] = self.scientific_name_id_urn + taxon_worms_info['aphia_id']
#                     occurrence_dict['kingdom'] = taxon_worms_info['kingdom']
#                     occurrence_dict['phylum'] = taxon_worms_info['phylum']
#                     occurrence_dict['class'] = taxon_worms_info['class']
#                     occurrence_dict['order'] = taxon_worms_info['order']
#                     occurrence_dict['family'] = taxon_worms_info['family']
#                     occurrence_dict['genus'] = taxon_worms_info['genus']
#                     occurrence_dict['specificEpithet'] = '' # TODO:
#                     occurrence_dict['scientificNameAuthorship'] = taxon_worms_info['authority']
#             #
#             occurrence_dict['collectionCode'] = self.collection_code
#             occurrence_dict['country'] = 'Sweden'
#             occurrence_dict['countryCode'] = 'SE'
#             #
#             self.dwca_occurrence.append(occurrence_dict)
#             self.dwca_occurrence_lookup[occurrence_key_string] = occurrence_dict
# 
#         # Add 'individualCount' and 'sampling effort' info.
#         if self.individual_count_parameter: 
#             if (row_dict['parameter'] == self.individual_count_parameter) and (row_dict['unit'] == self.individual_count_unit):
# #                 for searchrow_dict in self.dwca_occurrence:
# #                     if searchrow_dict['id'] == occurrence_key_string:
# #                         searchrow_dict['individualCount'] = row_dict.get('value', '')
# #                         break # Exit for-loop.
#                 self.dwca_occurrence_lookup[occurrence_key_string]['individualCount'] = row_dict.get('value', '')
#             
#             
#     def createArchivePartMeasurementorfact(self, row_dict, 
#                                            event_key_string, 
#                                            occurrence_key_string, 
#                                            measurementorfact_key_string, 
#                                            measurementorfact_key_list):
#         """ Concrete method. """
#         # Don't add parameters with no species. TODO: Maybe later as extra info on each row.
#         if not row_dict.get('scientific_name', None):
#             return
# 
#         if measurementorfact_key_string and (measurementorfact_key_string not in measurementorfact_key_list):
#             # One in occurrence.txt, the rest in measurementorfact.txt. Skip "# counted".
#             if self.individual_count_parameter:
#                 if (row_dict['parameter'] == self.individual_count_parameter) and (row_dict['unit'] == self.individual_count_unit):
#                     return # This one should only be used in the occurrence table.
#             #
#             measurementorfact_key_list.append(measurementorfact_key_string)
#             #
#             measurementorfact_dict = {}
#             # Direct field mapping.
#             for column_name in self.getDwcaMeasurementorfactColumns():
#                 if column_name in self.getDwcaDefaultMapping():
#                     measurementorfact_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], '')
#             # Add more.
#             measurementorfact_dict['id'] = self.measurementorfact_seq_no
#             self.measurementorfact_seq_no += 1
#             measurementorfact_dict['occurrenceID'] = occurrence_key_string
#             #
#             measurementorfact_dict['measurementType'] = row_dict['parameter']
#             measurementorfact_dict['measurementValue'] = row_dict['value']
#             measurementorfact_dict['measurementUnit'] = row_dict['unit']
#             
# #             # TODO: Remove this later. ERROR in Bacterioplankton data.
# #             if row_dict['unit'] == 'fgCcell': measurementorfact_dict['measurementType'] = 'fg C/cell'
# #             if row_dict['unit'] == 'µm3cell': measurementorfact_dict['measurementUnit'] = 'µm3/cell'
# #             if row_dict['unit'] == 'cellsl': measurementorfact_dict['measurementUnit'] = 'cells/l'
# #             if row_dict['unit'] == 'cellsld': measurementorfact_dict['measurementUnit'] = 'cells/l/d'
# 
#             # Zooplankton. EurOBIS don't like the same parameter name for ind/m2 and ind/m3. 
#             if (row_dict['parameter'] == 'Abundance') and (row_dict['unit'] == 'ind/m2'): 
#                 measurementorfact_dict['measurementType'] = 'Abundance/area'
#             if (row_dict['parameter'] == 'Abundance') and (row_dict['unit'] == 'ind/m3'): 
#                 measurementorfact_dict['measurementType'] = 'Abundance/volume'
#             #
#             self.dwca_measurementorfact.append(measurementorfact_dict)
#         #
#         else:
#             pass
#             # TODO: For development only. Remove in production. 
#             if row_dict['unit'] == 'ind/m3':
#                 pass # Too much...
#             else:
#                 if measurementorfact_key_string:
#                     print('DEBUG: Duplicate key in measurementorfact: ' + measurementorfact_key_string)
# 
# 
# 
# # class DarwinCoreArchiveFormatForSampleData(DarwinCoreArchiveFormat):
# #     """ """
# # 
# #     def __init__(self, datatype, settings_file_name = None, settings_dir_path = None,
# #                  meta_file_name = '', eml_file_name = '',
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
# #         direct_map = self.settings['direct_mapping']
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
# #             event_key_string = self.createKeyString(row_dict, self.settings['indata_event_keys']) 
# #             occurrence_key_string = self.createKeyString(row_dict, self.settings['indata_occurrence_keys']) 
# #             measurementorfact_key_string = self.createKeyString(row_dict, self.settings['indata_measurementorfact_keys'])             
# #             # Darwin Core: Event.
# #             if event_key_string and (event_key_string not in event_key_list):
# #                 event_key_list.append(event_key_string)
# #                 #
# #                 event_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings['event_columns']:
# #                     if column_name in direct_map:
# #                         event_dict[column_name] = row_dict.get(direct_map[column_name], '')
# #                 # Add more.
# #                 event_dict['id'] = event_seq_no
# #                 event_seq_no += 1
# #                 event_dict['eventID'] = event_key_string
# #                 event_dict['samplingProtocol'] = 'Protocol for ' + row_dict['datatype'] # ???
# #                 event_dict['type'] = 'Sampling event' # ???
# #     
# #                 event_dict['month'] = row_dict['visit_date'][5:7]
# #                 event_dict['month'] = row_dict['visit_date'][5:7]
# #                 event_dict['day'] = row_dict['visit_date'][8:10] 
# #                 event_dict['country'] = 'Sweden'
# #                 event_dict['countryCode'] = 'SE'                
# #                 #
# #                 self.dwca_event.append(event_dict) 
# #                 
# #             # Darwin Core: Occurrence.
# #             if occurrence_key_string and (occurrence_key_string not in occurrence_key_list):
# #                 occurrence_key_list.append(occurrence_key_string)
# #                 #
# #                 occurrence_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings['occurrence_columns']:
# #                     if column_name in direct_map:
# #                         occurrence_dict[column_name] = row_dict.get(direct_map[column_name], '')
# #                 # Add more.
# #                 occurrence_dict['id'] = occurrence_seq_no
# #                 occurrence_seq_no += 1
# #                 occurrence_dict['eventID'] = event_key_string
# #                 occurrence_dict['occurrenceID'] = occurrence_key_string
# # 
# #                 occurrence_dict['quantity'] = row_dict['value']
# #                 if row_dict['unit']:
# #                     occurrence_dict['quantityType'] = row_dict['parameter'] + ' (' + row_dict['unit'] + ')'
# #                 else:
# #                     occurrence_dict['quantityType'] = row_dict['parameter']
# #                 occurrence_dict['country'] = 'Sweden'
# #                 occurrence_dict['countryCode'] = 'SE'                
# #                 #
# #                 self.dwca_occurrence.append(occurrence_dict) 
# #                 
# #             # Darwin Core: Measurementorfact.
# #             if measurementorfact_key_string and (measurementorfact_key_string not in measurementorfact_key_list):
# #                 measurementorfact_key_list.append(measurementorfact_key_string)
# #                 #
# #                 measurementorfact_dict = {}
# #                 # Direct field mapping.
# #                 for column_name in self.settings['measurementorfact_columns']:
# #                     if column_name in direct_map:
# #                         measurementorfact_dict[column_name] = row_dict.get(direct_map[column_name], '')
# #                 # Add more.
# #                 measurementorfact_dict['id'] = measurementorfact_seq_no
# #                 measurementorfact_seq_no += 1
# #                 #    
# #                 self.dwca_measurementorfact.append(measurementorfact_dict) 
