#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.db import models

class Datasets(models.Model):
    """ Database table definition for datasets. 
        Datasets are stored in the FTP area. Datasets should follow
        the SHARK Archive Format both in file name and content.
    """
    #
    dataset_name  = models.CharField(max_length = 255)
    datatype = models.CharField(max_length = 63)
    version  = models.CharField(max_length = 63)
    dataset_file_name  = models.CharField(max_length = 255)
    ftp_file_path  = models.CharField(max_length = 1023)
    #
    content_data = models.TextField() # BinaryField()
    content_metadata = models.TextField() # BinaryField()
    content_metadata_auto = models.TextField() # BinaryField()
    #
    column_data_available = models.BooleanField(default = False)
    # Darwin Core Archives.
    dwc_archive_available = models.BooleanField(default = False)
    dwc_archive_file_path = models.CharField(max_length = 1023)
    dwc_archive_eurobis_available = models.BooleanField(default = False)
    dwc_archive_eurobis_file_path = models.CharField(max_length = 1023)
    dwc_archive_sampledata_available = models.BooleanField(default = False)
    dwc_archive_sampledata_file_path = models.CharField(max_length = 1023)
    #
    uploaded_by = models.CharField(max_length= 255)
    uploaded_datetime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.dataset_name
