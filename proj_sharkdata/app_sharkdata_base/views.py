#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import app_datasets.models as datasets_models
import app_speciesobs.models as speciesobs_models

def viewDocumentation(request):
    """ """
    first_dataset = None
    if datasets_models.Datasets.objects.count() > 0:
        first_dataset = datasets_models.Datasets.objects.all().order_by(u'dataset_name')[0]
    if first_dataset:
        first_dataset_name = first_dataset.dataset_name
    else:
        first_dataset_name = u'SHARK_Example_dataset'
    #    
    first_species_name = None
    species_names = speciesobs_models.SpeciesObs.objects.values_list(u'taxon_species', flat = True).distinct().order_by(u'taxon_species')
    for species_name in species_names:
        if (not first_species_name) and (len(species_name) > 5): # To avoid trash names like '-'.
            first_species_name = species_name
    if not first_species_name:
        first_species_name = u'Incertae sedis'
    #    
    return render_to_response("documentation.html", 
                              {u'first_dataset_name': first_dataset_name,
                               u'first_species_name': first_species_name})

def viewExampleCode(request):
    """ """    
    return render_to_response("examplecode.html")

def viewDataPolicy(request):
    """ """    
    return render_to_response("datapolicy.html")

def viewAbout(request):
    """ """    
    number_of_datasets = datasets_models.Datasets.objects.count()
    #
    return render_to_response("about.html", 
                              {'number_of_datasets': number_of_datasets})

