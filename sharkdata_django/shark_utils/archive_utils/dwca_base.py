#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2015 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import misc_utils
from django.conf import settings

class DwcaBase(object):
    """ """
    
    def __init__(self):
        """ Darwin Core Archive Format base class. """
        #
        self.worms_info_object = None
        #
        self.sampling_effort_items = {}
        self.sampling_protocol_items = {}
        self.dynamic_properties_items = {}
        self.identification_qualifier_items = {}
        self.field_number_items = []
        self.generated_parameters = {}
        #
        self.debug_missing_taxa = []
        #
        self.clear()

    def clear(self):
        """ """
        self.dwca_event_columns = []
        self.dwca_occurrence_columns = []
        self.dwca_measurementorfact_columns = []
        #
        self.indata_event_key_columns = []
        self.indata_occurrence_keys = []
        self.indata_measurementorfact_key_columns = []
        #
        self.dwca_default_mapping = []
        #
        self.dwca_event = [] 
        self.dwca_occurrence  = [] 
        self.dwca_measurementorfact  = [] 
        #
        self.dwca_occurrence_lookup  = {} # For fast access via key.


    def setWormsInfoObject(self, worms_info_object):
        """ For translations from scientific names to aditional WoRMS info. """
        self.worms_info_object = worms_info_object

    def getDwcaEventColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getDwcaOccurrenceColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getDwcaMeasurementorfactColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getIndataEventKeyColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getIndataOccurrenceKeyColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getIndataMeasurementorfactKeyColumns(self):
        """ Default implementation if not defined in subclass. """
        return []

    def getDwcaDefaultMapping(self):
        """ Default implementation if not defined in subclass. """
        return {}


    def createArchiveParts(self, dataset):
        """ Template method. Check http://en.wikipedia.org/wiki/Template_method_pattern """
        self.clear()
        # Lists of used key strings to group rows and avoid duplicates.
        event_key_list = []
        occurrence_key_list = []
        measurementorfact_key_list = []
        generated_parameters_key_list = []
        # Sequence numbers for id columns.
        self.event_seq_no = 0
        self.occurrence_seq_no = 0
        self.measurementorfact_seq_no = 0
        # Get header and iterate over rows in the dataset.
        header = dataset.data_header
        for row in dataset.data_rows:
            # Connect header and row content to a dictionary for easy access.
            row_dict = dict(zip(header, row))
            # Create key strings.
            event_key_string = self.createKeyString(row_dict, self.getIndataEventKeyColumns()) 
            occurrence_key_string = self.createKeyString(row_dict, self.getIndataOccurrenceKeyColumns()) 
            measurementorfact_key_string = self.createKeyString(row_dict, self.getIndataMeasurementorfactKeyColumns())
                
            # Darwin Core: Event.
            self.createArchivePartEvent(row_dict, 
                                        event_key_string, 
                                        occurrence_key_string, 
                                        measurementorfact_key_string, 
                                        event_key_list)                
            # Darwin Core: Occurrence.
            self.createArchivePartOccurrence(row_dict,
                                             event_key_string, 
                                             occurrence_key_string, 
                                             measurementorfact_key_string, 
                                             occurrence_key_list)
            # Darwin Core: Measurementorfact.
            self.createArchivePartMeasurementorfact(row_dict, 
                                                    event_key_string, 
                                                    occurrence_key_string, 
                                                    measurementorfact_key_string, 
                                                    measurementorfact_key_list,
                                                    generated_parameters_key_list)
        #
        if settings.DEBUG:
            if self.debug_missing_taxa:
                for taxon in sorted(self.debug_missing_taxa):
                    print(u'DEBUG: Missing taxa: ' + taxon)

    def createArchivePartEvent(self, row_dict, 
                               event_key_string, 
                               occurrence_key_string, 
                               measurementorfact_key_string, 
                               event_key_list):
        """ Concrete method. Default implementation if not defined in subclass. """

        if event_key_string and (event_key_string not in event_key_list):
            event_key_list.append(event_key_string)
            #
            event_dict = {}
            # Direct field mapping.
            for column_name in self.getDwcaEventColumns():
                if column_name in self.getDwcaDefaultMapping():
                    event_dict[column_name] = row_dict.get(self.getDwcaDefaultMapping()[column_name], u'')
            # Add more.
            event_dict[u'id'] = self.event_seq_no
            self.event_seq_no += 1
            #
            self.dwca_event.append(event_dict) 
            
    def createArchivePartOccurrence(self, row_dict, 
                                    event_key_string, 
                                    occurrence_key_string, 
                                    measurementorfact_key_string, 
                                    occurrence_key_list, 
                                    occurrence_seq_no):
        """ Abstract method. """
        
        raise UserWarning("The method createArchivePartOccurrence() is not implemented in subclass.")
            
    def createArchivePartMeasurementorfact(self, row_dict, 
                                           event_key_string, 
                                           occurrence_key_string, 
                                           measurementorfact_key_string, 
                                           measurementorfact_key_list,
                                           generated_parameters_key_list):
        """ Abstract method. """
        
        raise UserWarning("The method createArchivePartMeasurementorfact() is not implemented in subclass.")


    def saveToArchiveFile(self, file_path_name, zip_dir_path, settings_dir_path):
        """ """
        # Darwin Core Archive parts.
        event_content = [] 
        occurrence_content = [] 
        measurementorfact_content = []
         
        # Append headers for Event, Occurrence and Measurementorfact.
        event_content.append(u'\t'.join(self.getDwcaEventColumns())) 
        occurrence_content.append(u'\t'.join(self.getDwcaOccurrenceColumns())) 
        measurementorfact_content.append(u'\t'.join(self.getDwcaMeasurementorfactColumns()))
        
        # Convert from dictionary to row for each item in the list.
        # Event. 
        for row_dict in self.dwca_event:
            row = []
            for column_name in self.getDwcaEventColumns():
                row.append(unicode(row_dict.get(column_name, u'')))
            event_content.append(u'\t'.join(row))
        # Occurrence.
        for row_dict in self.dwca_occurrence:
            row = []
            for column_name in self.getDwcaOccurrenceColumns():
                row.append(unicode(row_dict.get(column_name, u'')))
            occurrence_content.append(u'\t'.join(row))
        # Measurementorfact.
        for row_dict in self.dwca_measurementorfact:
            row = []
            for column_name in self.getDwcaMeasurementorfactColumns():
                row.append(unicode(row_dict.get(column_name, u'')))
            measurementorfact_content.append(u'\t'.join(row))
                
        # Create zip archive.
        ziparchive = misc_utils.ZipArchive(file_path_name, zip_dir_path)
        if len(event_content) > 1:
            ziparchive.appendZipEntry(u'event.txt', (u'\r\n'.join(event_content).encode(u'utf-8')))
        if len(occurrence_content) > 1:
            ziparchive.appendZipEntry(u'occurrence.txt', (u'\r\n'.join(occurrence_content).encode(u'utf-8')))
        if len(measurementorfact_content) > 1:
            ziparchive.appendZipEntry(u'measurementorfact.txt', (u'\r\n'.join(measurementorfact_content).encode(u'utf-8')))
            
        # Add meta.xml files to zip.
        if self.meta_file_name:
            django_dir = os.path.dirname(__file__)
            meta_file_path_name = os.path.join(django_dir, self.xml_templates_path, self.meta_file_name)
            if os.path.exists(meta_file_path_name):
                ziparchive.appendFileAsZipEntry(u'meta.xml', meta_file_path_name)

        # Add eml.xml files to zip.
        if self.eml_file_name:
            django_dir = os.path.dirname(__file__)
            eml_file_path_name = os.path.join(django_dir, self.xml_templates_path, self.eml_file_name)
            if os.path.exists(eml_file_path_name):
                ziparchive.appendFileAsZipEntry(u'eml.xml', eml_file_path_name)

    def createKeyString(self, row_dict, key_columns):
        """ Util: Generates the key for one row. """
        key_string = u''
        try:
            key_list = [unicode(row_dict.get(item, u'')) for item in key_columns]
            key_string = u'+'.join(key_list)
        except:
            key_string = u'ERROR: Failed to generate key-string'
        # Replace swedish characters.
        key_string = key_string.replace(u'Å', u'A')
        key_string = key_string.replace(u'Ä', u'A')
        key_string = key_string.replace(u'Ö', u'O')
        key_string = key_string.replace(u'å', u'a')
        key_string = key_string.replace(u'ä', u'a')
        key_string = key_string.replace(u'ö', u'o')
        key_string = key_string.replace(u'µ', u'u')
        #
        return key_string

