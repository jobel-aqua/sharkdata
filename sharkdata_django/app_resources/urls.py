#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.conf.urls import patterns, include, url

urlpatterns = patterns('app_resources.views',
        (r'^$', 'listResources'),
        (r'^list$', 'listResources'),
        (r'^list.json$', 'listResourcesJson'),
        #
        (r'^table$', 'tableResources'),
        (r'^table.txt$', 'tableResourcesText'),
        (r'^table.json$', 'tableResourcesJson'),
        #
        (r'^import$', 'importResource'),
        #
        (r'^delete_all$', 'deleteResources'),
        (r'^delete/(?P<resource_id>\d+)$', 'deleteResource'),
        #
        (r'^load_all$', 'loadAllResources'),
        #
        (r'^(?P<resource_name>\S+)/content.txt$', 'resourceContentText'),
    )
