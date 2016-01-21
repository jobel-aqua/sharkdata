#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        (r'^$', include('app_datasets.urls')), # Use the dataset app as default.
        (r'^datasets/', include('app_datasets.urls')),
        (r'^resources/', include('app_resources.urls')),
        (r'^speciesobs/', include('app_speciesobs.urls')),
        (r'^documentation/', 'app_sharkdata_base.views.viewDocumentation'),
        (r'^datapolicy/', 'app_sharkdata_base.views.viewDataPolicy'),
        (r'^about/', 'app_sharkdata_base.views.viewAbout'),
    )
