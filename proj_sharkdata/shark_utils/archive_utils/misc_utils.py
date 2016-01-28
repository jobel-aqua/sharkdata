#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).


# TODO: Under development...


import os
import os.path
import codecs
import locale
import zipfile
from django.core.exceptions import ObjectDoesNotExist

excel_support = True 
try: import openpyxl 
except: excel_support = False 

xml_support = True
try: from lxml import etree 
except: xml_support = False

import app_resources.models as resources_models
 
"""
"""

class SpeciesWormsInfo():
    """ 
    """
    def __init__(self):
        """ """
        self.clear()
        self.species_dict = {}
        
    def clear(self):
        """ """
        self.species_dict = {}
         
    def getTaxonInfoDict(self, scientific_name):
        """ """
        return self.species_dict.get(scientific_name, None)
         
    def loadSpeciesFromResource(self):
        """ """
        self.clear()
        #
        resource = None
        try:
            resource = resources_models.Resources.objects.get(resource_name = u'taxa_worms_info')
        except ObjectDoesNotExist:
            resource = None
        if resource:
            header_row = None
#             data_as_text = resource.file_content.encode(u'cp1252')
            data_as_text = resource.file_content
            for index, row in enumerate(data_as_text.split(u'\n')):
                if index == 0:
                    header_row = [item.strip() for item in row.split(u'\t')]
                else:
                    row = [item.strip() for item in row.split(u'\t')]
                    row_dict = dict(zip(header_row, row))
                    if row_dict.get(u'Scientific name', None):
                        taxon_dict = {}
                        taxon_dict[u'aphia_id'] = row_dict.get(u'WORMS AphiaID', u'')
                        taxon_dict[u'kingdom'] = row_dict.get(u'WORMS Kingdom', u'')
                        taxon_dict[u'phylum'] = row_dict.get(u'WORMS Phylum', u'')
                        taxon_dict[u'class'] = row_dict.get(u'WORMS Class', u'')
                        taxon_dict[u'order'] = row_dict.get(u'WORMS Order', u'')
                        taxon_dict[u'family'] = row_dict.get(u'WORMS Family', u'')
                        taxon_dict[u'genus'] = row_dict.get(u'WORMS Genus', u'')
#                         taxon_dict[u'specific_epithet'] = row_dict.get(u'WORMS specific_epithet', u'')
                        taxon_dict[u'authority'] = row_dict.get(u'WORMS Authority', u'')
                        #
                        if taxon_dict[u'aphia_id']:
                            self.species_dict[row_dict[u'Scientific name']] = taxon_dict
                    
         
class Dataset():
    """ 
    Contains header and rows for the table based dataset. 
    Metadata is handled as a key/value dictionary. (TODO: NOT IMPLEMENTED...)
    """

    def __init__(self):
        """ """
        self.clearData()
        self.clearMetadata()
        
    def clearData(self):
        """ """
        self.data_header = None
        self.data_rows = []
         
    def clearMetadata(self):
        """ """
        self.metadata_dict = {}
        
    def loadDataFromZipFile(self, 
                            zip_file_name,
                            zip_entry = u'shark_data.txt', 
                            dataset_dir_path = None, 
                            encoding = None, 
                            header_row = 0, 
                            data_rows_from = 1):
        """ """
        self.clearData()
        # Check.
        if zip_file_name == None:
            raise UserWarning("Zip file name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        #
        if dataset_dir_path:
            zip_file_path = os.path.join(dataset_dir_path, zip_file_name)
        else:
            zip_file_path = zip_file_name

        # Read data.
        zip_file = None
        try:
            zip_file = zipfile.ZipFile(zip_file_path, 'r') 
            #
            fieldseparator = None
            # Iterate over rows in file.            
            for rowindex, row in enumerate(zip_file.open(zip_entry).readlines()):
                # Convert to unicode.
                row = unicode(row, encoding, 'strict')
                if rowindex == header_row:
                    # Header.
                    fieldseparator = self.getSeparator(row)
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_header =row
                elif rowindex >= data_rows_from:
                    # Row.
                    if len(row.strip()) == 0: 
                        continue # Don't add empty rows.
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_rows.append(row)             
        #
        finally:
            if zip_file: zip_file.close()

    def loadDataFromTextFile(self, 
                             dataset_file_name, 
                             dataset_dir_path = None, 
                             encoding = None, 
                             header_row = 0, 
                             data_rows_from = 1):
        """ """
        self.clearData()
        # Check.
        if dataset_file_name == None:
            raise UserWarning("File name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        #
        if dataset_dir_path:
            dataset_file_path = os.path.join(dataset_dir_path, dataset_file_name)
        else:
            dataset_file_path = dataset_file_name

        # Read file.
        infile = None
        try:
            infile = open(dataset_file_path, u'r')
            fieldseparator = None
            # Iterate over rows in file.            
            for rowindex, row in enumerate(infile):
                # Convert to unicode.
                row = unicode(row, encoding, 'strict')
                if rowindex == header_row:
                    # Header.
                    fieldseparator = self.getSeparator(row)
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_header =row
                elif rowindex >= data_rows_from:
                    # Row.
                    if len(row.strip()) == 0: 
                        continue # Don't add empty rows.
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_rows.append(row)             
        #
        finally:
            if infile: infile.close()

    def writeDataToTextFile(self, 
                            file_name,
                            encoding = None,
                            field_separator = u'\t',
                            row_separator = u'\r\n'):
        """ """
        # Check.
        if file_name == None:
            raise UserWarning("File name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        # Write to file.
        outfile = None
        try:
            outfile = codecs.open(file_name, mode = 'w', encoding = encoding)
            # Header.
            outfile.write(field_separator.join(map(unicode, self.data_header)) + row_separator)
            # Rows.
            for row in self.data_rows:
                outfile.write(field_separator.join(map(unicode, row)) + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write to text file: " + file_name)
        finally:
            if outfile: outfile.close()

    def getSeparator(self, row):
        """ Check the header row for used delimiter. """
        if u'\t' in row: return u'\t' # First alternative.
        elif u';' in row: return u';'# Second alternative. 
        else: return u'\t' # Default alternative.
        
    def loadDataFromExcel(self, 
                          file_name,
                          sheet_name = None, 
                          header_row = 0, 
                          data_rows_from = 1, 
                          data_rows_to = None): # None = read all.
        """ """
        if not excel_support:
            raise UserWarning("Excel not supported. Please install openpyxl")
        if file_name == None:
            raise UserWarning("File name is missing.")
        try:
            workbook = openpyxl.load_workbook(file_name, use_iterators = True) # Supports big files.
            if workbook == None:
                raise UserWarning("Can't read Excel (.xlsx) file.")
            worksheet = None
            if sheet_name:
                # 
                if sheet_name in workbook.get_sheet_names():
                    worksheet = workbook.get_sheet_by_name(name = sheet_name)
                else:
                    raise UserWarning("Excel sheet " + sheet_name + " not available.")      
            else:
                # Use the first sheet if not specified.
                worksheet = workbook.get_sheet_by_name(name = workbook.get_sheet_names()[0])
            #
            header = []
            for rowindex, row in enumerate(worksheet.iter_rows()): ### BIG.
                if data_rows_to and (rowindex > data_rows_to):
                    break # Break loop if data_row_to is defined and exceeded.
                elif rowindex == header_row:
                    for cell in row:
                        value = cell.internal_value
                        if value == None:
                            header.append(u'')
                        else:
                            header.append(unicode(value).strip())
                    self.data_header = header
                elif rowindex >= data_rows_from:
                    newrow = []
                    for cell in row:
                        value = cell.internal_value
                        if value == None:
                            newrow.append(u'')
                        else:
                            newrow.append(unicode(value).strip())
                    self.data_rows.append(newrow)
        #  
        except Exception:
            raise UserWarning("Can't read Excel file. File name: " + file_name)
 
    def writeDataToExcel(self, file_name):
        """ """
        if not excel_support:
            raise UserWarning("Excel not supported. Please install openpyxl")
        if file_name == None:
            raise UserWarning("File name is missing.")
        try:
            workbook =  openpyxl.Workbook(optimized_write = True)  # Supports big files.
            worksheet = workbook.create_sheet()
            # Header.
            worksheet.append(self.data_header)
            # Rows.
            for row in self.data_rows:
                worksheet.append(row)
            # Save to file.   
            workbook.save(file_name)
        #
        except (IOError, OSError):
            raise UserWarning("Failed to write to file: " + file_name)


class ZipArchive():
    """ """
    def __init__(self, zip_file_name, zip_dir_path = None):
        """ """
        if zip_dir_path:
            self._filepathname = os.path.join(zip_dir_path, zip_file_name)
        else:
            self._filepathname = zip_file_name
        # Delete old version, if exists.
        if os.path.exists(self._filepathname):
            os.remove(self._filepathname)

    def appendZipEntry(self, zip_entry_name, content):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.writestr(zip_entry_name, content)
        finally:
            if ziparchive:
                ziparchive.close()

    def appendFileAsZipEntry(self, zip_entry_name, file_path):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.write(file_path, zip_entry_name)
        finally:
            if ziparchive:
                ziparchive.close()


class XmlFileCreator(object):
    """ Creates XML file from XSLT template. """
    def __init__(self):
        """ """
        self.xslt_file_path = os.path.join(u'settings', 'shark_metadata_iso_19139.xslt')

    def metadataToIso19139(self, metadata_as_text):
        """ Metadata to XML. """
        metadata_as_xml = self._metadataTextToXml(metadata_as_text, rootname = "SharkMetadata")
        print('\n\n' + 'Metadata as XML: ' + etree.tostring(metadata_as_xml))
         
        # Transform.
        xsl_file = os.path.abspath(self.xslt_file_path).replace('\\','/')
        xsl = etree.parse(xsl_file)
        xslt = etree.XSLT(xsl)
        metadata_as_iso19139 =  xslt(metadata_as_xml)
        #
        print('\n\n' + str(metadata_as_iso19139))
        return metadata_as_iso19139
     
    def _metadataTextToXml(self, metadata_as_text, rootname):
        """ Transform a metadata record to a flat XML string. """
     
        metadata_dict = {}
        for row in metadata_as_text.split(u'\r\n'):
            if u':' in row:
                parts = row.split(u':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_dict[key] = value
        
        root = etree.Element(rootname)
     
        for key in metadata_dict.keys():
            
            col=key
            dat=''
            try:
                dat=str(metadata_dict[key]) # may need to be careful of unicode encoding issues when reading data from Excel
            except:
                ####dat=str(metadata_dict[key.decode(u'cp1252', u'replace')])
                dat=str('ERROR when decoding.')
                
            # TODO: Split on '#' to create lists. Used for lists of Parameters/units.
        
            if '#' not in key:

                child=etree.SubElement(root,col)
                child.text=dat

        return root

        # EXAMPLE CODE:
        # 
        # <root atr="100">
        #   text1
        #   <child atr="atr">
        #     <superchild atr="">sctext1</superchild>
        #     tail1
        #     tail2
        #   </child>
        #   tail
        #   <child atr="">text</child>
        # </root>
        # 
        # root = Element('root', atr=str(100))
        # root.text = 'text1'
        # child = SubElement(root, 'child', atr="atr")
        # superchild = SubElement(root, 'superchild', atr="" if value is None else value)
        # superchild.text = 'sctext1'
        # superchild.tail = 'tail1'
        # superchild.tail += 'tail2'
        # child.tail = 'tail'
        # child = SubElement(root, 'child', atr="")
        # child.text = 'text'


