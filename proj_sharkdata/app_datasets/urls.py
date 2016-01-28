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
        (r'^table.txt', 'tableDatasetsText'),
        (r'^table.json', 'tableDatasetsJson'),
        (r'^table.xml', 'datasetMetadataXml'),
        #
#         (r'^import$', 'importDataset'),
#         (r'^delete_all$', 'deleteDatasets'),
#         (r'^load_all$', 'loadAllDatasets'),
        (r'^delete/(?P<dataset_id>\d+)$', 'deleteDataset'),
        #
        (r'^(?P<dataset_name>\S+)/data.txt', 'datasetDataText'),
        (r'^(?P<dataset_name>\S+)/data.json', 'datasetDataJson'),
        (r'^(?P<dataset_name>\S+)/data_columns.txt', 'datasetDataColumnsText'),
        (r'^(?P<dataset_name>\S+)/data_columns.json', 'datasetDataColumnsJson'),
        #
        (r'^(?P<dataset_name>\S+)/metadata.txt', 'datasetMetadataText'),
        (r'^(?P<dataset_name>\S+)/metadata.json', 'datasetMetadataJson'),
        (r'^(?P<dataset_name>\S+)/metadata.xml', 'datasetMetadataXml'),
        #
        (r'^(?P<dataset_name>\S+)/shark_archive.zip', 'sharkArchiveZip'),
        # Darwin Core Archives.
        (r'^(?P<dataset_name>\S+)/dwc_archive.zip', 'dwcArchiveZip'),
        (r'^(?P<dataset_name>\S+)/dwc_archive_eurobis.zip', 'dwcArchiveEurobisZip'),
        (r'^(?P<dataset_name>\S+)/dwc_archive_sampledata.zip', 'dwcArchiveSampledataZip'),
    )
