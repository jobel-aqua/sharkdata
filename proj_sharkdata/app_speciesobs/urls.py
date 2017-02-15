#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import url
import app_speciesobs.views

urlpatterns = [
    # HTML pages.
    url(r'^$', app_speciesobs.views.listSpeciesObs),
    url(r'^list/', app_speciesobs.views.listSpeciesObs),
    url(r'^table/', app_speciesobs.views.tableSpeciesObsText),
    
    # Text and JSON.
    url(r'^table.txt', app_speciesobs.views.tableSpeciesObsText),
    url(r'^table.json', app_speciesobs.views.tableSpeciesObsJson),
    
#     # Positions.
#     url(r'^positions.kml', app_speciesobs.views.positionsKml),
#     url(r'^year_info.kml', app_speciesobs.views.yearInfoKml),
#     url(r'^map', app_speciesobs.views.mapOpenlayers),
]
