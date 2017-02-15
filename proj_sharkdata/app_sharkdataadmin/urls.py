#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import url
import app_sharkdataadmin.views

urlpatterns = [
    url(r'^$', app_sharkdataadmin.views.sharkDataAdmin),

    url(r'^datasets_delete_all/', app_sharkdataadmin.views.deleteDatasets),
    url(r'^datasets_load_all/', app_sharkdataadmin.views.loadAllDatasets),
    #
    url(r'^generate_archives/', app_sharkdataadmin.views.generateArchives),
    #
    url(r'^generate_ices_xml/', app_sharkdataadmin.views.generateIcesXml),
    url(r'^validate_ices_xml/', app_sharkdataadmin.views.validateIcesXml),
    url(r'^exportfiles_delete_all/', app_sharkdataadmin.views.deleteExportFiles),
    #
    url(r'^resources_delete_all/', app_sharkdataadmin.views.deleteResources),
    url(r'^resources_load_all/', app_sharkdataadmin.views.loadAllResources),
    #
    url(r'^speciesobs_update/', app_sharkdataadmin.views.updateSpeciesObs),
    url(r'^speciesobs_cleanup/', app_sharkdataadmin.views.cleanUpSpeciesObs),
    #
    url(r'^view_log/(?P<log_id>\d+)/', app_sharkdataadmin.views.viewLog),

]
