#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import zipfile
import tempfile
import shutil

class SharkArchiveFileReader(object):
    """ """
    def __init__(self, filename,
                 filepath = u''):
        """ """
        super(SharkArchiveFileReader, self).__init__()
        #
        self._filepathname = filename
        if filepath:
            self._filepathname = os.path.join(filepath, filename)
        #
        self._zip = None
        if not zipfile.is_zipfile(self._filepathname):
            raise UserWarning('Selected file is not a valid zip file: ' + self._filepathname)
        #

    def open(self):
        """ """
        self._zip = zipfile.ZipFile(self._filepathname, 'r')

    def close(self):
        """ """
        self._zip.close()
        self._zip = None

    def listContent(self):
        """ """
        if self._zip is None:
            self.open()    
        if self._zip:
            return self._zip.namelist()
        else:
            return {}

    def getDataAsText(self):
        """ """
        if self._zip is None:
            self.open()    
        if u'shark_data.txt' not in self._zip.namelist():
            raise UserWarning('The entry shark_data.txt is missing in ' + self._filepathname)
        #    
        return self._zip.open(u'shark_data.txt').read()

    def getDataColumnsAsText(self):
        """ """
        if self._zip is None:
            self.open()    
        if u'shark_data_columns.txt' not in self._zip.namelist():
            raise UserWarning('The entry shark_data_columns.txt is missing in ' + self._filepathname)
        #    
        return self._zip.open(u'shark_data_columns.txt').read()

    def getDataAsTable(self, target_table):
        """ """
#         if self._zip is None:
#             self.open()    
#         if u'shark_data.txt' not self._zip.namelist():
#             raise UserWarning('The entry shark_data.txt is missing in ' + self._filepathname')
#         #    
#         return self._zip.open(u'shark_data.txt', 'r')

    def getMetadataAsText(self):
        """ """
        if self._zip is None:
            self.open()    
        if u'shark_metadata.txt' not in self._zip.namelist():
            raise UserWarning('The entry shark_metadata.txt is missing in ' + self._filepathname)
        #    
        return self._zip.open(u'shark_metadata.txt').read()

    def getMetadataAutoAsText(self):
        """ """
        if self._zip is None:
            self.open()    
        if u'shark_metadata_auto.txt' not in self._zip.namelist():
            raise UserWarning('The entry shark_metadata_auto.txt is missing in ' + self._filepathname)
        #    
        return self._zip.read(u'shark_metadata_auto.txt') 
        #return u'\r\n'.join(self._zip.open(u'shark_metadata_auto.txt').readlines())

    def isDataColumnsAvailable(self):
        """ """
        if self._zip is None:
            self.open()    
        if u'shark_data_columns.txt' in self._zip.namelist():
            return True
        #    
        return False


class SharkArchiveFileWriter(object):
    """ """
    def __init__(self, filename,
                 filepath = u''):
        """ """
        super(SharkArchiveFileWriter, self).__init__()
        #
        self._filename = filename
        self._filepathname = filename
        if filepath:
            self._filepathname = os.path.join(filepath, filename)
        #
        if not zipfile.is_zipfile(self._filepathname):
            raise UserWarning('Selected file is not a valid zip file: ' + self._filepathname)
        #
    
    def removeEntryFromZip(self, zip_file, entries):
        """ There is no method in Python for this. 
            Copy everything else to a temporary zip file and rename when finished. """
        tmpdir = tempfile.mkdtemp()
        try:
            new_tmp_file = os.path.join(tmpdir, 'tmp.zip')
            zip_read = zipfile.ZipFile(zip_file, 'r')
            zip_write = zipfile.ZipFile(new_tmp_file, 'w', zipfile.ZIP_DEFLATED)
            for item in zip_read.infolist():
                if item.filename not in entries:
                    data = zip_read.read(item.filename)
                    zip_write.writestr(item, data)
            #
            shutil.move(new_tmp_file, zip_file) # 
        finally:
            shutil.rmtree(tmpdir)
    
    def generateMetadataAuto(self,
                             encoding = u'cp1252',
                             fieldseparator = u'\t'):
        """ """
        # Remove the entry shark_metadata_auto.txt
        self.removeEntryFromZip(self._filepathname, ['shark_metadata_auto.txt'])
        
        
        zip = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append to existing file. 
        try:
            #
            year_index = None
            date_index = None
            longitude_index = None
            latitude_index = None
            parameter_index = None
            unit_index = None
            #    
            min_year = None
            max_year = None
            min_date = None
            max_date = None
            min_longitude = None
            max_longitude = None
            min_latitude = None
            max_latitude = None
            parameter_unit_list = []
            #
            for index, row in enumerate(zip.open(u'shark_data.txt').readlines()):
                # Convert to unicode and separate fields.
                row = unicode(row, encoding, 'strict')
                row = [item.strip() for item in row.split(fieldseparator)]
                if index == 0:
                    header = row
                    for item_index, item in enumerate(header):
                        
                        if item in [u'year', u'visit_year']: year_index = item_index
                        if item in [u'sampling_date', u'visit_date']: date_index = item_index
                        if item in [u'latitude_dd', u'lat_dd']: latitude_index = item_index
                        if item in [u'longitude_dd', u'long_dd']: longitude_index = item_index
                        if item in [u'parameter']: parameter_index = item_index
                        if item in [u'unit']: unit_index = index
                        #
                        max_index = max(year_index, date_index, longitude_index, latitude_index, parameter_index, unit_index)
                else:
                    if len(row) > max_index:
                        if year_index:
                            min_year = min(row[year_index], min_year) if min_year else row[year_index]
                            max_year = max(row[year_index], max_year) if max_year else row[year_index]
                        if date_index:                                             
                            min_date = min(row[date_index], min_date) if min_date else row[date_index]
                            max_date = max(row[date_index], max_date) if max_date else row[date_index]
                        if longitude_index:           
                            min_longitude = min(row[longitude_index], min_longitude) if min_longitude else row[longitude_index]
                            max_longitude = max(row[longitude_index], max_longitude) if max_longitude else row[longitude_index]
                        if latitude_index:
                            min_latitude = min(row[latitude_index], min_latitude) if min_latitude else row[latitude_index]
                            max_latitude = max(row[latitude_index], max_latitude) if max_latitude else row[latitude_index]
                        if parameter_index: 
                            param_unit = row[parameter_index] + u':' + row[unit_index]
                            if param_unit not in parameter_unit_list:
                                parameter_unit_list.append(param_unit)
            # 
            metadata_rows = []
            #
#            metadata_rows.append(u'dataset_name: ' + min_year)
            name, datatype, version = self.splitFilename(self._filename)
            metadata_rows.append(u'dataset_name: ' + name)
            metadata_rows.append(u'dataset_version: ' + version)
            metadata_rows.append(u'dataset_category: ' + datatype)
            metadata_rows.append(u'dataset_file_name: ' + self._filename)
            #
            if year_index:
                metadata_rows.append(u'min_year: ' + min_year)
                metadata_rows.append(u'max_year: ' + max_year)            
            if date_index:
                if not year_index:
                    metadata_rows.append(u'min_year: ' + min_date[0:4])
                    metadata_rows.append(u'max_year: ' + max_date[0:4])            
                metadata_rows.append(u'min_date: ' + min_date)
                metadata_rows.append(u'max_date: ' + max_date)                
            if latitude_index:           
                metadata_rows.append(u'min_latitude: ' + min_latitude.replace(u',', u'.'))
                metadata_rows.append(u'max_latitude: ' + max_latitude.replace(u',', u'.')   )                                               
            if longitude_index:           
                metadata_rows.append(u'min_longitude: ' + min_longitude.replace(u',', u'.'))
                metadata_rows.append(u'max_longitude: ' + max_longitude.replace(u',', u'.'))
            if parameter_index:
                for index, param_unit in enumerate(parameter_unit_list):
                    pair = param_unit.split(u':')
                    metadata_rows.append(u'parameter#' + unicode(index) + u': ' + pair[0])
                    metadata_rows.append(u'unit#' + unicode(index) + u': ' + pair[1])
            # Join rows and write to zip.
            metadata = u'\r\n'.join(metadata_rows)
            zip.writestr('shark_metadata_auto.txt', metadata)
        finally:
            zip.close()

    def splitFilename(self, file_name):
        """ """
        filename = os.path.splitext(file_name)[0]
        parts = filename.split(u'version')
        name = parts[0].strip(u'_').strip()
        version = parts[1].strip(u'_').strip() if len(parts) > 0 else u''
        #
        parts = filename.split(u'_')
        datatype = parts[1].strip(u'_').strip()
        #
        return name, datatype, version


class SharkArchive(object):
    """ """
    def __init__(self, archive_path):
        """ """
        super(SharkArchive, self).__init__()
        #
        self._archive_path = archive_path
        self._zipfiles = {} # Dictionary, key=file name, value = path and name.
        #
        self.update()
        
    def update(self):
        """ """
        for root, dirs, files in os.walk(self._archive_path):
            for filename in files:
                if filename.startswith(u'SHARK') and \
                   (u'version' in filename) and \
                   filename.endswith(u'.zip'):
#                     print os.path.join(root, filename)
                    self._zipfiles[filename] = os.path.join(root, filename)
        
    def getSharkArchiveFilenames(self):
        """ """
        return self._zipfiles.keys()
        
    def getLatestSharkArchiveFilenames(self):
        """ """
        latest = {}
        versions = {}
        for filename in self._zipfiles.keys():
            name, datatype, version = self.splitFilename(filename) 
            if name in latest:
                if versions[name] < version:
                    latest[name] = filename # Replace if later version. 
                    versions[name] = version # Replace if later version. 
            else:
                latest[name] = filename
                versions[name] = version
        #
        return sorted(latest.values())
        
    def getFullPathForFile(self, file_name):
        """ """
        return self._zipfiles.get(file_name, None)

    def splitFilename(self, file_name):
        """ """
        filename = os.path.splitext(file_name)[0]
        parts = filename.split(u'version')
        name = parts[0].strip(u'_').strip()
        version = parts[1].strip(u'_').strip() if len(parts) > 0 else u''
        #
        parts = filename.split(u'_')
        datatype = parts[1].strip(u'_').strip()
        #
        return name, datatype, version
        

# FOR DEVELOPMENT:
# def shark_archive_test():
#     """ """
#     archive = SharkArchive(u'/home/parallels/Desktop/SHARK_FTP/datasets')
#     for filename in archive.getSharkArchiveFilenames():
#         print(filename)
#         name, datatype, version = archive.splitFilename(filename)
#         print(name)
#         print(datatype)
#         print(version)
#      
#     print(u'-----')    
#          
#     for filename in archive.getLatestSharkArchiveFilenames():
#         print(filename)
#         name, datatype, version = archive.splitFilename(filename)
#         print(name)
#         print(datatype)
#         print(version)
#          
#     print(u'--- List shark-metadata-auto ---') 
#      
#     zipreader = SharkArchiveFileReader(u'SHARK_Speciesobs_2010_Zooplankton_version_TEST2013-11-10.zip', 
#                                        u'/home/parallels/Desktop/SHARK_FTP/datasets')
#     try:
#         zipreader.open()
#         for item in zipreader.listContent():
#             print(u'Content: ' + item)
#             
#         print(zipreader.getMetadataAutoAsText())    
#         
#     finally:
#         zipreader.close()
#         
#     print(u'--- Calculate shark-metadata-auto ---') 
#     
#     zipwriter = SharkArchiveFileWriter(u'SHARK_Speciesobs_2010_Zooplankton_version_TEST2013-11-10.zip', 
#                                        u'/home/parallels/Desktop/SHARK_FTP/datasets')
#     zipwriter.generateMetadataAuto()
#       
#     zipwriter = SharkArchiveFileWriter(u'SHARK_Speciesobs_2011_Zooplankton_version_TEST2013-11-10.zip', 
#                                        u'/home/parallels/Desktop/SHARK_FTP/datasets')
#     zipwriter.generateMetadataAuto()
#       
#     zipwriter = SharkArchiveFileWriter(u'SHARK_Speciesobs_2012_Zooplankton_version_TEST2013-11-10.zip', 
#                                        u'/home/parallels/Desktop/SHARK_FTP/datasets')
#     zipwriter.generateMetadataAuto()
#       
#     print(u'-----') 
#     
# 
# if __name__ == "__main__":
#     shark_archive_test()



