#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import copy
import dwca_base
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import app_resources.models as resources_models

class DwcaEurObis(dwca_base.DwcaBase):
    """ """

    def __init__(self):
        """ """
        #
        super(DwcaEurObis, self).__init__()
        #
        self.xml_templates_path = 'dwca_xml_templates'
        self.meta_file_name = 'meta_eurobis.xml'
        self.eml_file_name = 'eml_eurobis.xml'
        self.scientific_name_id_urn = 'urn:lsid:marinespecies.org:taxname:'
        
        self.translate_taxa = TranslateTaxa()
        self.translate_taxa.loadTranslateTaxaEurobis('translate_taxa_eurobis')
                
    def createArchivePartOccurrence(self, row_dict, 
                                    event_key_string, 
                                    occurrence_key_string, 
                                    measurementorfact_key_string, 
                                    occurrence_key_list):
        """ Concrete method. """
        # Don't add parameters with no species. TODO: Maybe later as extra info on each row.
        if not row_dict.get('scientific_name', None):
            return
        
        if occurrence_key_string and (occurrence_key_string not in occurrence_key_list):
            #
            occurrence_key_list.append(occurrence_key_string)
            #
            occurrence_dict = {}
            # Direct field mapping.
            for column_name in self.getDwcaOccurrenceColumns():
                if column_name in self.getDwcaDefaultMapping():
                    occurrence_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], '')
            # Add more.
            occurrence_dict['id'] = occurrence_key_string
            #
            occurrence_dict['year'] = row_dict['sample_date'][0:4]
            occurrence_dict['month'] = row_dict['sample_date'][5:7]
            occurrence_dict['day'] = row_dict['sample_date'][8:10] 
            occurrence_dict['country'] = 'Sweden'
            occurrence_dict['countryCode'] = 'SE'                
            #
            # Sampling effort.        
            if len(self.sampling_effort_items) > 0:
                sampling_effort_list = []
                for key, value in self.sampling_effort_items.items():
                    if row_dict.get(value, None):
                        sampling_effort_list.append(key + '=' + row_dict.get(value, ''))
                occurrence_dict['samplingEffort'] = '; '.join(sampling_effort_list)
            # Sampling protocol.        
            if len(self.sampling_protocol_items) > 0:
                sampling_protocol_list = []
                for key, value in self.sampling_protocol_items.items():
                    if row_dict.get(value, None):
                        sampling_protocol_list.append(key + '=' + row_dict.get(value, ''))
                occurrence_dict['samplingProtocol'] = '; '.join(sampling_protocol_list)
            # Dynamic properties. Used for Size classes in Phytoplancton etc.        
            if len(self.dynamic_properties_items) > 0:
                dynamic_properties_list = []
                for key, value in self.dynamic_properties_items.items():
                    if row_dict.get(value, None):
                        dynamic_properties_list.append(key + '=' + row_dict.get(value, ''))
                occurrence_dict['dynamicProperties'] = '; '.join(dynamic_properties_list)                 

            
            # Identification Qualifier. Used for species related qualifiers.       
            if len(self.identification_qualifier_items) > 0:
                identification_qualifier_list = []
                for key, value in self.identification_qualifier_items.items():
                    if row_dict.get(value, None):
                        identification_qualifier_list.append(key + '=' + row_dict.get(value, ''))
                occurrence_dict['identificationQualifier'] = '; '.join(identification_qualifier_list)                 
            
            
            # Field_number. Used for sample_id, sample_part_id, etc.        
            if len(self.field_number_items) > 0:
                field_number_list = []
                for key in self.field_number_items:
                    if row_dict.get(key, None):
                        field_number_list.append(row_dict.get(key, ''))
                occurrence_dict['fieldNumber'] = '-'.join(field_number_list)                 
            # Time zone info (+01:00 for Sweden).
            event_time = occurrence_dict['eventTime']
            if event_time != '':
                occurrence_dict['eventTime'] = event_time + '+01:00'
            
            #
            # Translate species name.
            shark_scientific_name = row_dict['scientific_name']
            eurobis_scientific_name = self.translate_taxa.getTranslatedTaxa(shark_scientific_name)
            occurrence_dict['scientificName'] = eurobis_scientific_name
            #
            # Add WoRMS data.
            if self.worms_info_object:
                taxon_worms_info = self.worms_info_object.getTaxonInfoDict(shark_scientific_name)
                if taxon_worms_info:
                    if taxon_worms_info['aphia_id']:
                        occurrence_dict['scientificNameID'] = self.scientific_name_id_urn + taxon_worms_info['aphia_id']
                    occurrence_dict['kingdom'] = taxon_worms_info['kingdom']
                    occurrence_dict['phylum'] = taxon_worms_info['phylum']
                    occurrence_dict['class'] = taxon_worms_info['class']
                    occurrence_dict['order'] = taxon_worms_info['order']
                    occurrence_dict['family'] = taxon_worms_info['family']
                    occurrence_dict['genus'] = taxon_worms_info['genus']
                    occurrence_dict['specificEpithet'] = '' # TODO:
                    occurrence_dict['scientificNameAuthorship'] = taxon_worms_info['authority']
                else:
                    if settings.DEBUG:
                        if row_dict['scientific_name'] not in self.debug_missing_taxa:
                            self.debug_missing_taxa.append(row_dict['scientific_name'])
            #
            occurrence_dict['collectionCode'] = self.collection_code
            occurrence_dict['country'] = 'Sweden'
            occurrence_dict['countryCode'] = 'SE'
            #
            self.dwca_occurrence.append(occurrence_dict)
            self.dwca_occurrence_lookup[occurrence_key_string] = occurrence_dict

        # Add 'individualCount' (self.dwca_occurrence_lookup is used).
        if self.individual_count_parameter:
            try: 
                if (row_dict['parameter'] == self.individual_count_parameter) and (row_dict['unit'] == self.individual_count_unit):
                    self.dwca_occurrence_lookup[occurrence_key_string]['individualCount'] = row_dict.get('value', '')
            except:
                pass # Don't stop if this happens.
            
            
    def createArchivePartMeasurementorfact(self, row_dict, 
                                           event_key_string, 
                                           occurrence_key_string, 
                                           measurementorfact_key_string, 
                                           measurementorfact_key_list,
                                           generated_parameters_key_list):
        """ Concrete method. """
        # Don't add parameters with no species. TODO: Maybe later as extra info on each row.
        if not row_dict.get('scientific_name', None):
            return

        if measurementorfact_key_string and (measurementorfact_key_string not in measurementorfact_key_list):
            # One in occurrence.txt, the rest in measurementorfact.txt. Skip "# counted".
            if self.individual_count_parameter:
                if (row_dict['parameter'] == self.individual_count_parameter) and (row_dict['unit'] == self.individual_count_unit):
                    return # This one should only be used in the occurrence table.
            #
            measurementorfact_key_list.append(measurementorfact_key_string)
            #
            measurementorfact_dict = {}
            # Direct field mapping.
            for column_name in self.getDwcaMeasurementorfactColumns():
                if column_name in self.getDwcaDefaultMapping():
                    measurementorfact_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], '')
            # Add more.
            measurementorfact_dict['id'] = self.measurementorfact_seq_no
            self.measurementorfact_seq_no += 1
            measurementorfact_dict['occurrenceID'] = occurrence_key_string
            #
            measurementorfact_dict['measurementType'] = row_dict['parameter']
            measurementorfact_dict['measurementValue'] = row_dict['value']
            measurementorfact_dict['measurementUnit'] = row_dict['unit']
            
            # Zooplankton. EurOBIS don't like the same parameter name for ind/m2 and ind/m3. 
            if (row_dict['parameter'] == 'Abundance') and (row_dict['unit'] == 'ind/m2'): 
                measurementorfact_dict['measurementType'] = 'Abundance/area'
            if (row_dict['parameter'] == 'Abundance') and (row_dict['unit'] == 'ind/m3'): 
                measurementorfact_dict['measurementType'] = 'Abundance/volume'
            #
            # Quality_flag. 
            remarks = measurementorfact_dict['measurementRemarks'] 
            quality_flag = row_dict.get('quality_flag', '')
            if quality_flag != '':
                if remarks == '':
                    remarks = 'QualityFlag=' + quality_flag
                else:
                    remarks = 'QualityFlag=' + quality_flag + '; Remarks=' + remarks
                # 
                measurementorfact_dict['measurementRemarks'] = remarks
            #
            self.dwca_measurementorfact.append(measurementorfact_dict)
            
            # Parameters generated from column data.
            # Should only be done once for each row in the occurrence table.
            if occurrence_key_string not in generated_parameters_key_list:
                generated_parameters_key_list.append(occurrence_key_string)       
                if len(self.generated_parameters) > 0:
                    for key, value in self.generated_parameters.items():
                        if row_dict.get(value, None):
                            parameter = key
                            unit = ''
                            if ':' in key:
                                param_unit = key.split(':')
                                parameter = param_unit[0]
                                unit = param_unit[1]
                            #
                            measurementorfact_dict_2 = copy.deepcopy(measurementorfact_dict)
                            measurementorfact_dict_2['id'] = self.measurementorfact_seq_no
                            self.measurementorfact_seq_no += 1
                            #
                            measurementorfact_dict_2['measurementType'] = parameter
                            measurementorfact_dict_2['measurementValue'] = row_dict.get(value, '')
                            measurementorfact_dict_2['measurementUnit'] = unit
                            #
                            self.dwca_measurementorfact.append(measurementorfact_dict_2)
            
        #
        else:
            if settings.DEBUG:
                    if measurementorfact_key_string:
                        print('DEBUG: Duplicate key in measurementorfact: ' + measurementorfact_key_string)


class TranslateTaxa():
    """ """
    
    def __init__(self):
        """ """
        self.clear()
        
    def clear(self):
        """ """
        self.translate_taxa_dict = {}
         
    def getTranslatedTaxa(self, scientific_name):
        """ """
        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        else:
            return scientific_name
         
    def loadTranslateTaxaEurobis(self, resource_name):
        """ """
        self.clear()
        #
        resource = None
        try:
            resource = resources_models.Resources.objects.get(resource_name = resource_name)
        except ObjectDoesNotExist:
            resource = None
        if resource:
#             data_as_text = resource.file_content.encode('cp1252')
            data_as_text = resource.file_content
            for index, row in enumerate(data_as_text.split('\n')):
                if index == 0:
                    pass
                else:
                    row = [item.strip() for item in row.split('\t')]
                    #
                    if len(row) >= 2:
                        if row[0] and row[1]:
                            self.translate_taxa_dict[row[0]] = row[1]


