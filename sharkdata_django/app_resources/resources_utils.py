#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import os
import codecs
import shark_utils
from django.conf import settings
import app_resources.models as models
from django.core.exceptions import ObjectDoesNotExist

@shark_utils.singleton
class ResourcesUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, u'resources')
        self._resource_headers = None
        self._translated_headers = {}

    def clear(self):
        """ This must be called when new translate files are imported. """
        self._resource_headers = None
        self._translated_headers = {}
        
    def getHeaders(self):
        """ """
        if self._resource_headers == None:
            self._resource_headers = [
                        u'resource_name', 
                        u'resource_type', 
                        u'resource_file_name', 
                        u'encoding', 
#                       u'file_content', 
#                       u'uploaded_by', 
#                       u'uploaded_datetime', 
                        ]
        #
        return self._resource_headers

    def translateHeaders(self, data_header, 
                         resource_name = u'translate_headers', 
                         language = u'english'):
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

    def _getTranslateHeaders(self, resource_name = u'translate_headers', 
                            language = u'english'):
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
            for index, row in enumerate(data_as_text.split(u'\n')):
                if index == 0:
                    columnindex = None
                    for index2, column in enumerate(row.split(u'\t')):
                        if language == column.strip():
                            columnindex = index2
                else:
                    if columnindex:
                        rowitems = row.split(u'\t')
                        if len(rowitems) > columnindex:
                            translate_dict[rowitems[0].strip()] = rowitems[columnindex].strip()
        #
        self._translated_headers[(resource_name, language)] = translate_dict

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

    def deleteFileFromFtp(self, file_name):
        """ Delete resource from FTP area. """
        file_path = os.path.join(self._ftp_dir_path, file_name)
        # Delete the file.
        os.remove(file_path)

    def deleteAllFilesFromFtp(self):
        """ Delete all resources from FTP area. """
        for file_name in os.listdir(self._ftp_dir_path):
            file_path = os.path.join(self._ftp_dir_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def writeResourcesInfoToDb(self, user = u''):
        """ Updates the database from datasets stored in the FTP area.
            I multiple versions of a dataset are in the FTP area only the latest 
            will be loaded.
        """
        # Remove all db rows. 
        models.Resources.objects.all().delete()
        # Get resources from FTP archive.
        for file_name in self.getResourceFiles():
            self.writeFileInfoToDb(file_name, user)

    def writeFileInfoToDb(self, file_name, user = u''):
        """ Extracts info from the resource file name and add to database. """
        #
        ftp_file_path = os.path.join(self._ftp_dir_path, file_name)
        # Extract info from file name.
        resource_name, resource_type, encoding = self.splitFilename(file_name)
        #
        try:
            resource_file = codecs.open(ftp_file_path, u'r', encoding = encoding)
            resource_content = resource_file.read()
            resource_file.close()
        except:
            resource_content = u'ERROR'
        
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
        resource_name = filename.strip(u'_').strip()
        parts = filename.split(u'_')
        resource_type = parts[0].strip(u'_').strip()
        #
        encoding = u'windows-1252'
        if u'utf8' in filename.lower():
            encoding = u'utf-8'
        if u'utf-8' in filename.lower():
            encoding = u'utf-8'
        #
        return resource_name, resource_type, encoding

