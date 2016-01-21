#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.conf.urls import patterns, include, url

urlpatterns = patterns('app_speciesobs.views',
        # HTML pages.
        (r'^$', 'listSpeciesObs'),
        (r'^list$', 'listSpeciesObs'),
        (r'^table$', 'listSpeciesObs'),
        
        # Text and JSON.
        (r'^table.txt', 'tableSpeciesObsText'),
        (r'^table.json', 'tableSpeciesObsJson'),
        
        # Positions.
        (r'^positions.kml', 'positionsKml'),
        (r'^year_info.kml', 'yearInfoKml'),
        (r'^map', 'mapOpenlayers'),
        
#         # Commands from HTML pages.
#         (r'^update$', 'updateSpeciesObs'),
#         (r'^load$', 'loadSpeciesObs'),
#         (r'^cleanup$', 'cleanUpSpeciesObs'),
    )
