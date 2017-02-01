#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import include, url
import app_sharkdata_base.views

urlpatterns = [
    url(r'^about/', app_sharkdata_base.views.viewAbout),
    url(r'^documentation/',app_sharkdata_base.views.viewDocumentation),
    url(r'^examplecode/', app_sharkdata_base.views.viewExampleCode),
    url(r'^datapolicy/', app_sharkdata_base.views.viewDataPolicy),
    #
    url(r'^datasets/', include('app_datasets.urls')),
    url(r'^resources/', include('app_resources.urls')),
    url(r'^exportformats/', include('app_exportformats.urls')),
    url(r'^speciesobs/', include('app_speciesobs.urls')),
    url(r'^sharkdataadmin/', include('app_sharkdataadmin.urls')), 
    #
    url(r'^', include('app_datasets.urls')), # Default page.
]
