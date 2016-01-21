#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import threading
import shark_utils
from django.conf import settings
import app_datasets.models as models

@shark_utils.singleton
class DatasetUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._data_header = None
        self._translations = None
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'datasets')
        self._metadata_update_thread = None

    def getHeaders(self):
        """ """
        if not self._data_header:
            self._data_header = [
                        u'dataset_name', 
                        u'datatype', 
                        u'version', 
                        u'dataset_file_name', 
#                         u'ftp_file_path', 
#                         u'content_data', 
#                         u'content_metadata', 
#                         u'content_metadata_auto', 
#                         u'uploaded_by', 
#                         u'uploaded_datetime', 
                        ]
        #
        return self._data_header

    def translateHeaders(self, data_header, type = None):
        """ """
        translated = []
        #
        if not self._translations:
            self._translations = {
                        u'dataset_name': u'Dataset name', 
                        u'datatype': u'Datatype', 
                        u'version': u'Version', 
                        u'dataset_file_name': u'File name', 
#                         u'ftp_file_path': u'', 
#                         u'content_data': u'', 
#                         u'content_metadata': u'', 
#                         u'content_metadata_auto': u'', 
#                         u'uploaded_by': u'Uploaded by', 
#                         u'uploaded_datetime': u'', 
                        }            
        #
        for item in data_header:
            if item in self._translations:
                translated.append(self._translations[item])
            else:
                translated.append(item)
        #
        return translated

    def getDataAsText(self, dataset_name):
        """ Data is not stred in database, get from zip file."""
        db_dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        #
        # Extract data part.
        data_content = u''
        zipreader = shark_utils.SharkArchiveFileReader(db_dataset.dataset_file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            data_content = zipreader.getDataAsText().decode(u'cp1252') # Default encoding in archive data.

        finally:
            zipreader.close()                        
#             print(data_content)
        #
        return data_content
    
    def getMetadataAsText(self, dataset_name):
        """ """
        db_dataset = models.Datasets.objects.get(dataset_name=dataset_name)
        # Fix line breaks for windows. Remove rows with no key-value-pairs.
        metadata_list = []
        concat_metadata = db_dataset.content_metadata + u'\n' + db_dataset.content_metadata_auto
        for row in concat_metadata.split(u'\n'):
            if u':' in row:
                parts = row.split(u':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_list.append(key + u': ' + value)
        #
        return u'\r\n'.join(metadata_list)
    
    def saveUploadedFileToFtp(self, uploaded_file):
        """ Note: The parameter 'uploaded_file must' be of class UploadedFile. """
        file_name = unicode(uploaded_file)
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Save by reading/writing chunks..
        destination = open(file_path, 'wb+')
        try:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        finally:
            destination.close()
        return None # No error message.

    def deleteFileFromFtp(self, file_name):
        """ Delete all version of the dataset. """
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Delete the file.
        os.remove(file_path)
        #
        return None # No error message.

    def deleteAllFilesFromFtp(self):
        """ Delete all datasets from FTP area. """
        for file_name in os.listdir(self._ftp_dir_path):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                if file_name.startswith(u'SHARK') and file_name.endswith(u'.zip'):
                    os.remove(file_path)
        #
        return None # No error message.

    def writeLatestDatasetsInfoToDb(self, user = u''):
        """ Updates the database from datasets stored in the FTP area.
            I multiple versions of a dataset are in the FTP area only the latest 
            will be loaded.
        """
        # Remove all db rows. 
        models.Datasets.objects.all().delete()
        # Get latest datasets from FTP archive.
        archive = shark_utils.SharkArchive(self._ftp_dir_path)
        for file_name in archive.getLatestSharkArchiveFilenames():
            self.writeFileInfoToDb(file_name, user)
        #
        return None # No error message.

    def writeFileInfoToDb(self, file_name, user = u''):
        """ Extracts info from the dataset filename and from the zip file content and adds to database. """
        #
        ftp_file_path = os.path.join(self._ftp_dir_path, file_name)
        # Extract info from file name.
        dataset_name, datatype, version = self.splitFilename(file_name)
        # Extract metadata parts.
        metadata = u''
        metadata_auto = u''
        zipreader = shark_utils.SharkArchiveFileReader(file_name, self._ftp_dir_path)
        try:
            zipreader.open()
            metadata = zipreader.getMetadataAsText()
            metadata_auto = zipreader.getMetadataAutoAsText()                       
        finally:
            zipreader.close()                        
#             print(metadata_auto)
        # Save to db.
        dataset = models.Datasets(
                      dataset_name = dataset_name,
                      datatype = datatype,
                      version = version,
                      dataset_file_name = file_name,
                      ftp_file_path = ftp_file_path,
                      content_data = u'NOT USED',
                      content_metadata = metadata,
                      content_metadata_auto = metadata_auto,
                      )
        dataset.save()
        #
        return None # No error message.

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
        
    def updateMetadataForAllDatasetsInThread(self):
        """ """
        # Check if metadata update thread is running.
        if self._metadata_update_thread:
            if self._metadata_update_thread.is_alive():
                return u"Metadata update is already running. Please try again later."
        # Use a thread to relese the user. This will take some time.
        self._metadata_update_thread = threading.Thread(target = self.updateMetadataForAllDatasets)
        self._metadata_update_thread.start()
        #
        return None # No error message.
                
    def updateMetadataForAllDatasets(self):
        """ """
        archive = shark_utils.SharkArchive(self._ftp_dir_path)
        for file_name in archive.getLatestSharkArchiveFilenames():
            zipwriter = shark_utils.SharkArchiveFileWriter(file_name, self._ftp_dir_path)
            zipwriter.generateMetadataAuto()
        # Update database when finished.
        self.writeLatestDatasetsInfoToDb(u'')


