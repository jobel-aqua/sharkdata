#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import url
import app_datasets.views

urlpatterns = [
    url(r'^$', app_datasets.views.listDatasets),
    url(r'^list/', app_datasets.views.listDatasets),
    url(r'^list.json', app_datasets.views.listDatasetsJson),
    #
    url(r'^table/', app_datasets.views.tableDatasetsText),
    url(r'^table.txt/', app_datasets.views.tableDatasetsText),
    url(r'^table.json/', app_datasets.views.tableDatasetsJson),
    #
    url(r'^delete/(?P<dataset_id>\d+)', app_datasets.views.deleteDataset),
    #
    url(r'^(?P<dataset_name>\S+)/data.txt', app_datasets.views.datasetDataText),
    url(r'^(?P<dataset_name>\S+)/data.json', app_datasets.views.datasetDataJson),
    url(r'^(?P<dataset_name>\S+)/data_columns.txt', app_datasets.views.datasetDataColumnsText),
    url(r'^(?P<dataset_name>\S+)/data_columns.json', app_datasets.views.datasetDataColumnsJson),
    #
    url(r'^(?P<dataset_name>\S+)/metadata.txt', app_datasets.views.datasetMetadataText),
    url(r'^(?P<dataset_name>\S+)/metadata.json', app_datasets.views.datasetMetadataJson),
    url(r'^(?P<dataset_name>\S+)/metadata.xml', app_datasets.views.datasetMetadataXml),
    # SHARK Archives.
    url(r'^(?P<dataset_name>\S+)/shark_archive.zip', app_datasets.views.sharkArchiveZip),
    # Darwin Core Archives.
    url(r'^(?P<dataset_name>\S+)/dwc_archive.zip', app_datasets.views.dwcArchiveZip),
    url(r'^(?P<dataset_name>\S+)/dwc_archive_eurobis.zip', app_datasets.views.dwcArchiveEurobisZip),
    url(r'^(?P<dataset_name>\S+)/dwc_archive_sampledata.zip', app_datasets.views.dwcArchiveSampledataZip),
]
