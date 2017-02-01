#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import url
import app_resources.views

urlpatterns = [
    url(r'^$', app_resources.views.listResources),
    url(r'^list/', app_resources.views.listResources),
    url(r'^list.json/', app_resources.views.listResourcesJson),
    #
    url(r'^table/', app_resources.views.tableResourcesText),
    url(r'^table.txt/', app_resources.views.tableResourcesText),
    url(r'^table.json/', app_resources.views.tableResourcesJson),
    #
    url(r'^delete/(?P<resource_id>\d+)', app_resources.views.deleteResource),
    #
    url(r'^(?P<resource_name>\S+)/content.txt', app_resources.views.resourceContentText),
]
