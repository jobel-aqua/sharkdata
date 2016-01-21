#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import time
import json

from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml
from django.conf import settings
import app_speciesobs.models as models
import app_datasets.models as datasets_models
import app_speciesobs.forms as forms
import shark_utils
import app_speciesobs.speciesobs_utils as speciesobs_utils
import django.core.paginator as paginator
import app_sharkdataadmin.models as admin_models


def listSpeciesObs(request):
    """ """    
    error_message = None # initially.
    #
    header_language = request.GET.get('header_language', 'darwin_core')
    data_header = speciesobs_utils.SpeciesObsUtils().getHeaders()
    translated_headers = speciesobs_utils.SpeciesObsUtils().translateHeaders(data_header, 
                                                                             language = header_language)
    #
    data_rows = None
    #
    if request.method == "GET":
        form = forms.SpeciesObsFilterForm()
        contextinstance = {'form': form,
                           'data_header' : None,
                           'data_rows' : None,
                           'url_table' : None,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("list_speciesobs.html", contextinstance)
    elif request.method == "POST":
        if request.POST['confirm'] == "get_data":
            form = forms.SpeciesObsFilterForm(request.POST)
            #
            db_filter_dict = {}
            url_param_list = []
            forms.parse_filter_params(request.POST, db_filter_dict, url_param_list) 
            #
            data_rows = []
            # Check parameters to avoid too long queries.
            class_param = u''
            order_param = u''
            species_param = u''
            scientific_name_param = u''
            if u'class' in request.POST:
                class_param = request.POST['class']
            if u'order' in request.POST:
                order_param = request.POST['order']
            if u'species' in request.POST:
                species_param = request.POST['species']
            if u'scientific_name' in request.POST:
                scientific_name_param = request.POST['scientific_name']
            # Check for empty or '-'.
            if ((class_param not in [u'All', u'-', u'']) or 
                (order_param not in [u'All', u'-', u'']) or 
                (species_param not in [u'All', u'-', u'']) or 
                (scientific_name_param not in [u'All', u'-', u''])):
                #
                # Only show ACTIVE rows as a part of the HTML page.
                db_filter_dict[u'status__iexact'] = u'ACTIVE'
                data_rows = models.SpeciesObs.objects.values_list(*data_header).filter(**db_filter_dict)
                #
                if not data_rows:
                    error_message = u'No data found. Please try again...'

            else:
                error_message = u'At least one of Scientific name, Class, Order or Species must be selected. Please select one and try again...'
            #
            contextinstance = {'form': form,
                               'data_header' : data_header,
                               'data_rows' : data_rows,
                               'url_table' : None,
                               'error_message' : error_message}
            contextinstance.update(csrf(request))
            return render_to_response("list_speciesobs.html", contextinstance)
        #
        if request.POST['confirm'] == "view_url":
            #
            db_filter_dict = {}
            url_param_list = []
            forms.parse_filter_params(request.POST, db_filter_dict, url_param_list)
            url_params = u'' 
            if url_param_list:
                url_params += u'?'
                url_params += u'&'.join(url_param_list)
            #
            url_table = []
            if u'?' in url_params:
                url_table.append(u'/speciesobs/table.txt/' + url_params + u'&page=1&per_page=10')
                url_table.append(u'/speciesobs/table.json/' + url_params + u'&page=1&per_page=10')
                url_table.append(u'/speciesobs/table.json/' + url_params + u'&page=1&per_page=10&view_deleted=true')
            else:
                url_table.append(u'/speciesobs/table.txt/' + url_params + u'?page=1&per_page=10')
                url_table.append(u'/speciesobs/table.json/' + url_params + u'?page=1&per_page=10')
                url_table.append(u'/speciesobs/table.json/' + url_params + u'?page=1&per_page=10&view_deleted=true')
            url_table.append(u'---')
            url_table.append(u'/speciesobs/table.txt/' + url_params)
            url_table.append(u'/speciesobs/table.json/' + url_params)
            url_table.append(u'/speciesobs/positions.kml/' + url_params)
            url_table.append(u'/speciesobs/year_info.kml/' + url_params)
            url_table.append(u'/speciesobs/map/' + url_params)
#             url_table.append(u'http://maps.google.se/?q=http://sharkdata.se/speciesobs/positions.kml/' + url_params)
#             url_table.append(u'http://maps.google.se/?q=http://sharkdata.se/speciesobs/year_info.kml/' + url_params)
#             
#             url_table.append(u'---')
#             url_table.append(u'For development (from http://test.sharkdata.se):')
#             url_table.append(u'http://maps.google.se/?q=http://test.sharkdata.se/speciesobs/positions.kml/' + url_params)
#             url_table.append(u'http://maps.google.se/?q=http://test.sharkdata.se/speciesobs/year_info.kml/' + url_params)
            #
            form = forms.SpeciesObsFilterForm(request.POST)
            contextinstance = {'form': form,
                               'data_header' : None,
                               'data_rows' : None,
                               'url_table' : url_table,
                               'error_message' : error_message}
            contextinstance.update(csrf(request))
            return render_to_response("list_speciesobs.html", contextinstance)
    #
    return HttpResponseRedirect("/speciesobs")

def tableSpeciesObsText(request):
    """ """
    # Check if pagination.
    pagination_page = request.GET.get('page', None)
    pagination_size = request.GET.get('per_page', 100) # Default 100.
    #
    header_language = request.GET.get('header_language', 'darwin_core')
    data_header = speciesobs_utils.SpeciesObsUtils().getHeaders()
    translated_headers = speciesobs_utils.SpeciesObsUtils().translateHeaders(data_header, 
                                                                             language = header_language)
    #
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows, if not all status is requested.
    if request.GET.get('view_deleted', u'false') != u'true':
        db_filter_dict[u'status__iexact'] = u'ACTIVE'
    #
    data_rows = models.SpeciesObs.objects.values_list(*data_header).filter(**db_filter_dict)
    #
    if pagination_page: 
        pag = paginator.Paginator(data_rows, pagination_size)
        try:
            data_rows = pag.page(pagination_page)
        except paginator.EmptyPage:
            # If page is out of range, return header only.
            data_rows = []
    #
    response = HttpResponse(content_type = 'text/plain; charset=utf8')    
    response['Content-Disposition'] = 'attachment; filename=species_observations.txt'    
    response.write(u'\t'.join(translated_headers) + u'\r\n') # Tab separated.
    for row in data_rows:
        response.write(u'\t'.join(row) + u'\r\n') # Tab separated.        
    return response
    
def tableSpeciesObsJson(request):
    """ """
    # Check if pagination.
    pagination_page = request.GET.get('page', None)
    pagination_size = request.GET.get('per_page', 100) # Default 100.
    #
    header_language = request.GET.get('header_language', 'darwin_core')
    data_header = speciesobs_utils.SpeciesObsUtils().getHeaders()
    translated_headers = speciesobs_utils.SpeciesObsUtils().translateHeaders(data_header, 
                                                                             language = header_language)
    #
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows, if not all status is requested.
    if request.GET.get('view_deleted', u'false') != u'true':
        db_filter_dict[u'status__iexact'] = u'ACTIVE'
    #
    data_rows = models.SpeciesObs.objects.values_list(*data_header).filter(**db_filter_dict)
    #
    if pagination_page: 
        pag = paginator.Paginator(data_rows, pagination_size)
        try:
            data_rows = pag.page(pagination_page)
        except paginator.EmptyPage:
            # If page is out of range, return header only.
            data_rows = []
    #
    response = HttpResponse(content_type = 'application/json; charset=utf8')
    response['Content-Disposition'] = 'attachment; filename=species_observations.json'    
    response.write(u'{')
    if pagination_page and pag: 
        response.write(u'"page": ' + unicode(pagination_page) + u', ')
        response.write(u'"pages": ' + unicode(pag.num_pages) + u', ')
        response.write(u'"per_page": ' + unicode(pagination_size) + u', ')
        response.write(u'"total": ' + unicode(pag.count) + u', ')
    response.write(u'"header": ["')
    response.write(u'", "'.join(translated_headers) + u'"], ') # Tab separated.
    response.write(u'"rows": [')
    row_delimiter = u''
    for row in data_rows:
        response.write(row_delimiter + u'["' + '", "'.join(row) + u'"]')      
        row_delimiter = u', '
    response.write(u']')
    response.write(u'}')

    return response

def positionsKml(request):
    """ """
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows as a part of the KML file.
    db_filter_dict[u'status__iexact'] = u'ACTIVE'
    observations  = models.SpeciesObs.objects.kml().filter(**db_filter_dict)
    #
    # Extract and aggregate data.
    taxon_pos_dict = {}
    for obs in observations:
        taxon_pos_key = (obs.scientific_name, obs.latitude_dd, obs.longitude_dd)
        if taxon_pos_key not in taxon_pos_dict:
            taxon_pos_dict[taxon_pos_key] = obs.kml # Geographic point in KML format.
    #
    # Reformat to match the template "positions_kml.kml".
    kml_name = u'SHARKdata: Marine species observations.'
    kml_description = """
        Data source: <a href="http://sharkdata.se">http://sharkdata.se</a> <br>
    """ 
    #
    kml_data = []
    for key in sorted(taxon_pos_dict.keys()):
        scientific_name, latitude, longitude = key
        #
        kml_descr = u'<p>'
        kml_descr += u'Scientific name: ' + scientific_name + u'<br>'
        kml_descr += u'Latitude: ' + latitude + u'<br>'
        kml_descr += u'Longitude: ' + longitude + u'<br>'
        kml_descr += u'</p>'
        #
        row_dict = {}
        row_dict[u'kml_name'] = scientific_name
        row_dict[u'kml_description'] = kml_descr
        row_dict[u'kml_kml'] = taxon_pos_dict[key] # Geographic point in KML format.
        kml_data.append(row_dict)
        
    return render_to_kml("positions_kml.kml", {'kml_name' : kml_name,
                                             'kml_description' : kml_description,
                                             'kml_data' : kml_data})
 
def yearInfoKml(request):
    """ """
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows as a part of the KML file.
    db_filter_dict[u'status__iexact'] = u'ACTIVE'
    observations  = models.SpeciesObs.objects.kml().filter(**db_filter_dict)
    #
    # Extract and aggregate data.
    year_datatype_taxon_pos_dict = {}
    obsdict = None
    for obs in observations:
        year_datatype_taxon_pos_key = (obs.sampling_year, obs.data_type, obs.scientific_name, obs.longitude_dd, obs.latitude_dd)
        if year_datatype_taxon_pos_key not in year_datatype_taxon_pos_dict:
            obsdict = {}
            obsdict[u'counter'] = 0
            obsdict[u'sampling_month_set'] = set()
            year_datatype_taxon_pos_dict[year_datatype_taxon_pos_key] = obsdict
            
        #
        obsdict = year_datatype_taxon_pos_dict[year_datatype_taxon_pos_key]
        obsdict[u'data_type'] = obs.data_type
        obsdict[u'sampling_year'] = obs.sampling_year
        obsdict[u'taxon_kingdom'] = obs.taxon_kingdom
        obsdict[u'taxon_phylum'] = obs.taxon_phylum
        obsdict[u'taxon_class'] = obs.taxon_class
        obsdict[u'taxon_order'] = obs.taxon_order
        obsdict[u'scientific_name'] = obs.scientific_name
        obsdict[u'latitude_dd'] = obs.latitude_dd
        obsdict[u'longitude_dd'] = obs.longitude_dd
        obsdict[u'counter'] += 1
        obsdict[u'sampling_month_set'].add(obs.sampling_month)
        obsdict[u'kml_kml'] = obs.kml # Geographic point in KML format.
    #
    
    # Reformat to match the template "species_kml.kml".
    kml_name = u'SHARKdata: Marine species observations.'
    kml_description = """
        Data source: <a href="http://sharkdata.se">http://sharkdata.se</a> <br>
    """ 
    #
    kml_data = []
    last_used_year = None
    year_dict = {}
    for key in sorted(year_datatype_taxon_pos_dict.keys()):
        year_taxon_pos = year_datatype_taxon_pos_dict[key]
        data_type = year_taxon_pos[u'data_type']
        year = year_taxon_pos[u'sampling_year']
        taxon_kingdom = year_taxon_pos[u'taxon_kingdom']
        taxon_phylum = year_taxon_pos[u'taxon_phylum']
        taxon_class = year_taxon_pos[u'taxon_class']
        taxon_order = year_taxon_pos[u'taxon_order']
        scientific_name = year_taxon_pos[u'scientific_name']
        latitude_dd = year_taxon_pos[u'latitude_dd']
        longitude_dd = year_taxon_pos[u'longitude_dd']
        counter = unicode(year_taxon_pos[u'counter'])
        sampling_month = u', '.join(sorted(year_taxon_pos[u'sampling_month_set']))
        kml_kml = year_taxon_pos[u'kml_kml'] # Geographic point in KML format.
        #
        if (last_used_year == None) or (last_used_year != year) :
            last_used_year = year
            year_dict = {}
            year_dict[u'kml_name'] = u'Year: ' + year + u' Category: ' + data_type
            year_dict[u'rows'] = []  
            kml_data.append(year_dict)
        #
        row_dict = {}
        row_dict[u'kml_name'] = scientific_name
        #
        kml_descr = u'<p>'
        if data_type:
            kml_descr += u'Category: ' + data_type + u'<br>'
        if taxon_kingdom:
            kml_descr += u'Kingdom: ' + taxon_kingdom + u'<br>'
        if taxon_phylum:
            kml_descr += u'Phylum: ' + taxon_phylum + u'<br>'
        if taxon_class:
            kml_descr += u'Class: ' + taxon_class + u'<br>'
        if taxon_order:
            kml_descr += u'Order: ' + taxon_order + u'<br>'
        kml_descr += u'Scientific name: ' + scientific_name + u'<br>'
        kml_descr += u'Year: ' + year + u'<br>'
        kml_descr += u'Latitude: ' + latitude_dd + u'<br>'
        kml_descr += u'Longitude: ' + longitude_dd + u'<br>'
        kml_descr += u'Number of samples: ' + counter + u'<br>'
        kml_descr += u'Months observed: ' + sampling_month + u'<br>'
        kml_descr += u'</p>'
        
        row_dict[u'kml_description'] = kml_descr 
        row_dict[u'kml_kml'] = kml_kml 
        year_dict[u'rows'].append(row_dict)
        
    return render_to_kml("year_info_kml.kml", {'kml_name' : kml_name,
                                             'kml_description' : kml_description,
                                             'kml_data' : kml_data})
 
def mapOpenlayers(request):
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    url_params = u'' 
    if url_param_list:
        url_params += u'?'
        url_params += u'&'.join(url_param_list)
    kml_link = u'/speciesobs/positions.kml/' + url_params
    # Only show ACTIVE rows.
    db_filter_dict[u'status__iexact'] = u'ACTIVE'
    observations_count  = models.SpeciesObs.objects.kml().filter(**db_filter_dict).count()
    
    return render_to_response('speciesobs_map.html', {'kml_link' : kml_link,
                                                      'location_count' : observations_count}) 

# def updateSpeciesObs(request):
#     """ Updates species observations based of content in the datasets. """
#     #
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         #
#         form = forms.UpdateSpeciesObsForm()
#         return render_to_response("update_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : None})
#     elif request.method == "POST":
#         form = forms.UpdateSpeciesObsForm(request.POST)
#         if form.is_valid():
#             #
#             user = request.POST['user']
#             password = request.POST['password']
#             if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
#                 error_message = u'Not a valid user or password. Please try again...'   
#             #
#             if error_message == None:
#                 try:
#                     error_message = speciesobs_utils.SpeciesObsUtils().updateSpeciesObsInThread()
#                 except:
#                     error_message = u"Can't update species observations from datasets."
#                      
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/speciesobs")
#         #
#         return render_to_response("update_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : error_message})
#     # Not a valid request method.
#     return HttpResponseRedirect("/speciesobs")
    
# def loadSpeciesObs(request):
#     """ Load species observations from file. """
#     #
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         #
#         form = forms.LoadSpeciesObsForm()
#         return render_to_response("load_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : None})
#     elif request.method == "POST":
#         form = forms.LoadSpeciesObsForm(request.POST)
#         if form.is_valid():
#             #
#             user = request.POST['user']
#             password = request.POST['password']
#             if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
#                 error_message = u'Not a valid user or password. Please try again...'   
#             #
#             if error_message == None:
#                 try:
#                     error_message = speciesobs_utils.SpeciesObsUtils().loadSpeciesObsInThread()
#                 except:
#                     error_message = u"Can't load species observations from file."
#                      
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/speciesobs")
#         #
#         return render_to_response("load_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : error_message})
#     # Not a valid request method.
#     return HttpResponseRedirect("/speciesobs")
    
    
# def cleanUpSpeciesObs(request):
#     """ Removes species observations with status='DELETED'. """
#     #
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         #
#         form = forms.CleanUpSpeciesObsForm()
#         return render_to_response("clean_up_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : None})
#     elif request.method == "POST":
#         form = forms.CleanUpSpeciesObsForm(request.POST)
#         if form.is_valid():
#             #
#             user = request.POST['user']
#             password = request.POST['password']
#             if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
#                 error_message = u'Not a valid user or password. Please try again...'   
#             #
#             if error_message == None:
#                 try:
#                     error_message = speciesobs_utils.SpeciesObsUtils().cleanUpSpeciesObsInThread()
#                 except:
#                     error_message = u"Can't clean up species observations."
#                      
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/speciesobs")
#         #
#         return render_to_response("clean_up_speciesobs.html",
#                                   {'form'   : form,
#                                    'error_message' : error_message})
#     # Not a valid request method.
#     return HttpResponseRedirect("/speciesobs")
