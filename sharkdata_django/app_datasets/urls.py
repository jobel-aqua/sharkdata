#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.conf.urls import patterns, include, url

urlpatterns = patterns('app_datasets.views',
        (r'^$', 'listDatasets'),
        (r'^list$', 'listDatasets'),
        (r'^list.json$', 'listDatasetsJson'),
        #
        (r'^table$', 'tableDatasets'),
        (r'^table.txt$', 'tableDatasetsText'),
        (r'^table.json$', 'tableDatasetsJson'),
        #
        (r'^import$', 'importDataset'),
        #
        (r'^delete_all$', 'deleteDatasets'),
        (r'^delete/(?P<dataset_id>\d+)$', 'deleteDataset'),
        #
        (r'^load_all$', 'loadAllDatasets'),
        #
        (r'^(?P<dataset_name>\S+)/data.txt$', 'datasetDataText'),
        (r'^(?P<dataset_name>\S+)/data.json$', 'datasetDataJson'),
        #
        (r'^(?P<dataset_name>\S+)/metadata.txt$', 'datasetMetadataText'),
        (r'^(?P<dataset_name>\S+)/metadata.json$', 'datasetMetadataJson'),
        (r'^(?P<dataset_name>\S+)/metadata.xml$', 'datasetMetadataXml'),
    )
