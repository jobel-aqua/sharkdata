#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import codecs
from django.conf import settings
import app_resources.models as models
from django.core.exceptions import ObjectDoesNotExist
import sharkdata_core

@sharkdata_core.singleton
class ResourcesUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'resources')
        self._resource_headers = None
        self._translated_headers = {}

    def clear(self):
        """ This must be called when new translate files are imported. """
        self._resource_headers = None
        self._translated_headers = {}
        
    def getResourceListHeaders(self):
        """ """
        if self._resource_headers == None:
            self._resource_headers = [
                        'resource_name', 
                        'resource_type', 
                        'resource_file_name', 
                        'encoding', 
#                       'file_content', 
#                       'uploaded_by', 
#                       'uploaded_datetime', 
                        ]
        #
        return self._resource_headers

    def translateHeaders(self, data_header, 
                         resource_name = 'translate_headers', 
                         language = 'english'):
        """ """
        if ((resource_name, language) not in self._translated_headers):
            self._getTranslateHeaders(resource_name, language)
        #
        translated = []
        translate_dict = self._translated_headers[(resource_name.strip(), language)]
        for item in data_header:
            translated.append(translate_dict.get(item.strip(), item.strip())) # Item value as default.
        #
        return translated

    def _getTranslateHeaders(self, resource_name = 'translate_headers', 
                             language = 'english'):
        """ """
        translate_dict = {}
        columnindex = None
        
        resource = None
        try:
            resource = models.Resources.objects.get(resource_name = resource_name)
        except ObjectDoesNotExist:
            resource = None
        if resource:
            data_as_text = resource.file_content
            for index, row in enumerate(data_as_text.split('\n')):
                if index == 0:
                    columnindex = None
                    for index2, column in enumerate(row.split('\t')):
                        if language == column.strip():
                            columnindex = index2
                else:
                    if columnindex:
                        rowitems = row.split('\t')
                        if len(rowitems) > columnindex:
                            translate_dict[rowitems[0].strip()] = rowitems[columnindex].strip()
        #
        self._translated_headers[(resource_name, language)] = translate_dict

    def saveUploadedFileToFtp(self, uploaded_file):
        """ Note: The parameter 'uploaded_file must' be of class UploadedFile. """
        self.clear()
        #
        file_name = unicode(uploaded_file)
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Save by reading/writing chunks..
        destination = open(file_path, 'wb+')
        try:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        finally:
            destination.close()

    def deleteFileFromFtp(self, file_name):
        """ Delete one resource from the FTP area. """
        self.clear()
        #
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Delete the file.
        os.remove(file_path)

    def deleteAllFilesFromFtp(self):
        """ Delete all resources from FTP area. """
        self.clear()
        #
        for file_name in os.listdir(self._ftp_dir_path):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def writeResourcesInfoToDb(self, user = ''):
        """ Updates the database from datasets stored in the FTP area.
            I multiple versions of a dataset are in the FTP area only the latest 
            will be loaded.
        """
        self.clear()
        # Remove all db rows. 
        models.Resources.objects.all().delete()
        # Get resources from FTP archive.
        for file_name in self.getResourceFiles():
            self.writeFileInfoToDb(file_name, user)

    def writeFileInfoToDb(self, file_name, user = ''):
        """ Extracts info from the resource file name and add to database. """
        #
        self.clear()
        #
        ftp_file_path = os.path.join(self._ftp_dir_path, file_name)
        # Extract info from file name.
        resource_name, resource_type, encoding = self.splitFilename(file_name)
        #
        try:
            resource_file = codecs.open(ftp_file_path, 'r', encoding = encoding)
            resource_content = resource_file.read()
            resource_file.close()
        except:
            resource_content = 'ERROR'
        
        # Save to db.
        resources = models.Resources(
                      resource_name = resource_name,
                      resource_type = resource_type,
                      encoding = encoding,
                      resource_file_name = file_name,
                      ftp_file_path = ftp_file_path,
                      file_content = resource_content,
                      uploaded_by = user
                      )
        resources.save()

    def getResourceFiles(self):
        """ Read filenames from FTP area. """
        resource_files = []
        for file_name in os.listdir(self._ftp_dir_path):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                resource_files.append(file_name)
        #
        return resource_files

    def splitFilename(self, file_name):
        """ Extract parts from file name. """
        filename = os.path.splitext(file_name)[0]
        resource_name = filename.strip('_').strip()
        parts = filename.split('_')
        resource_type = parts[0].strip('_').strip()
        #
        encoding = 'windows-1252'
        if 'utf8' in filename.lower():
            encoding = 'utf-8'
        if 'utf-8' in filename.lower():
            encoding = 'utf-8'
        #
        return resource_name, resource_type, encoding

