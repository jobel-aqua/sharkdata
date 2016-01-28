#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.conf.urls import patterns, include, url

urlpatterns = patterns('app_sharkdataadmin.views',
        (r'^$', 'sharkDataAdmin'),

#         (r'^datasets_import$', 'importDataset'),
        (r'^datasets_delete_all', 'deleteDatasets'),
        (r'^datasets_load_all', 'loadAllDatasets'),
        (r'^generate_archives', 'generateArchives'),

#         (r'^resources_import$', 'importResource'),
        (r'^resources_delete_all$', 'deleteResources'),
        (r'^resources_load_all$', 'loadAllResources'),

        (r'^speciesobs_update$', 'updateSpeciesObs'),
#         (r'^speciesobs_load$', 'loadSpeciesObs'),
        (r'^speciesobs_cleanup', 'cleanUpSpeciesObs'),
        
        (r'^view_log/(?P<log_id>\d+)$', 'viewLog'),

    )
