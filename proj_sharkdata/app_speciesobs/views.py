#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import time
import json

from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.template.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml
from django.conf import settings
import app_speciesobs.models as models
import app_datasets.models as datasets_models
import app_speciesobs.forms as forms
import django.core.paginator as paginator
import app_sharkdataadmin.models as admin_models
import sharkdata_core


def listSpeciesObs(request):
    """ """    
    error_message = None # initially.
    #
    header_language = request.GET.get('header_language', 'darwin_core')
    data_header = sharkdata_core.SpeciesObsUtils().getHeaders()
    translated_headers = sharkdata_core.SpeciesObsUtils().translateHeaders(data_header, 
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
            class_param = ''
            order_param = ''
            species_param = ''
            scientific_name_param = ''
            if 'class' in request.POST:
                class_param = request.POST['class']
            if 'order' in request.POST:
                order_param = request.POST['order']
            if 'genus' in request.POST:
                genus_param = request.POST['genus']
#             if 'species' in request.POST:
#                 species_param = request.POST['species']
            if 'scientific_name' in request.POST:
                scientific_name_param = request.POST['scientific_name']
            # Check for empty or '-'.
            if ((class_param not in ['All', '-', '']) or 
                (order_param not in ['All', '-', '']) or 
                (genus_param not in ['All', '-', '']) or 
#                 (species_param not in ['All', '-', '']) or 
                (scientific_name_param not in ['All', '-', ''])):
                #
                # Only show ACTIVE rows as a part of the HTML page.
                db_filter_dict['status__iexact'] = 'ACTIVE'
                data_rows = models.SpeciesObs.objects.values_list(*data_header).filter(**db_filter_dict)
                #
                if not data_rows:
                    error_message = 'No data found. Please try again...'

            else:
                error_message = 'At least one of Scientific name, Class, Order or Genus must be selected. Please select one and try again...'
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
            url_params = '' 
            if url_param_list:
                url_params += '?'
                url_params += '&'.join(url_param_list)
            #
            url_table = []
            if '?' in url_params:
                url_table.append('/speciesobs/table.txt/' + url_params + '&page=1&per_page=10')
                url_table.append('/speciesobs/table.json/' + url_params + '&page=1&per_page=10')
                url_table.append('/speciesobs/table.json/' + url_params + '&page=1&per_page=10&view_deleted=true')
            else:
                url_table.append('/speciesobs/table.txt/' + url_params + '?page=1&per_page=10')
                url_table.append('/speciesobs/table.json/' + url_params + '?page=1&per_page=10')
                url_table.append('/speciesobs/table.json/' + url_params + '?page=1&per_page=10&view_deleted=true')
            url_table.append('---')
            url_table.append('/speciesobs/table.txt/' + url_params)
            url_table.append('/speciesobs/table.json/' + url_params)
#             url_table.append('/speciesobs/positions.kml/' + url_params)
#             url_table.append('/speciesobs/year_info.kml/' + url_params)
#             url_table.append('/speciesobs/map/' + url_params)
            
#             url_table.append('http://maps.google.se/?q=http://sharkdata.se/speciesobs/positions.kml/' + url_params)
#             url_table.append('http://maps.google.se/?q=http://sharkdata.se/speciesobs/year_info.kml/' + url_params)
#             
#             url_table.append('---')
#             url_table.append('For development (from http://test.sharkdata.se):')
#             url_table.append('http://maps.google.se/?q=http://test.sharkdata.se/speciesobs/positions.kml/' + url_params)
#             url_table.append('http://maps.google.se/?q=http://test.sharkdata.se/speciesobs/year_info.kml/' + url_params)
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
    data_header = sharkdata_core.SpeciesObsUtils().getHeaders()
    translated_headers = sharkdata_core.SpeciesObsUtils().translateHeaders(data_header, 
                                                                             language = header_language)
    #
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows, if not all status is requested.
    if request.GET.get('view_deleted', 'false') != 'true':
        db_filter_dict['status__iexact'] = 'ACTIVE'
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
    response.write('\t'.join(translated_headers) + '\r\n') # Tab separated.
    for row in data_rows:
        response.write('\t'.join(row) + '\r\n') # Tab separated.        
    return response
    
def tableSpeciesObsJson(request):
    """ """
    # Check if pagination.
    pagination_page = request.GET.get('page', None)
    pagination_size = request.GET.get('per_page', 100) # Default 100.
    #
    header_language = request.GET.get('header_language', 'darwin_core')
    data_header = sharkdata_core.SpeciesObsUtils().getHeaders()
    translated_headers = sharkdata_core.SpeciesObsUtils().translateHeaders(data_header, 
                                                                             language = header_language)
    #
    db_filter_dict = {}
    url_param_list = []
    forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
    #
    # Only show ACTIVE rows, if not all status is requested.
    if request.GET.get('view_deleted', 'false') != 'true':
        db_filter_dict['status__iexact'] = 'ACTIVE'
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
    response.write('{')
    if pagination_page and pag: 
        response.write('"page": ' + unicode(pagination_page) + ', ')
        response.write('"pages": ' + unicode(pag.num_pages) + ', ')
        response.write('"per_page": ' + unicode(pagination_size) + ', ')
        response.write('"total": ' + unicode(pag.count) + ', ')
    response.write('"header": ["')
    response.write('", "'.join(translated_headers) + '"], ') # Tab separated.
    response.write('"rows": [')
    row_delimiter = ''
    for row in data_rows:
        response.write(row_delimiter + '["' + '", "'.join(row) + '"]')      
        row_delimiter = ', '
    response.write(']')
    response.write('}')

    return response

# def positionsKml(request):
#     """ """
#     db_filter_dict = {}
#     url_param_list = []
#     forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
#     #
#     # Only show ACTIVE rows as a part of the KML file.
#     db_filter_dict['status__iexact'] = 'ACTIVE'
#     observations  = models.SpeciesObs.objects.kml().filter(**db_filter_dict)
#     #
#     # Extract and aggregate data.
#     taxon_pos_dict = {}
#     for obs in observations:
#         taxon_pos_key = (obs.scientific_name, obs.latitude_dd, obs.longitude_dd)
#         if taxon_pos_key not in taxon_pos_dict:
#             taxon_pos_dict[taxon_pos_key] = obs.kml # Geographic point in KML format.
#     #
#     # Reformat to match the template "positions_kml.kml".
#     kml_name = 'SHARKdata: Marine species observations.'
#     kml_description = """
#         Data source: <a href="http://sharkdata.se">http://sharkdata.se</a> <br>
#     """ 
#     #
#     kml_data = []
#     for key in sorted(taxon_pos_dict.keys()):
#         scientific_name, latitude, longitude = key
#         #
#         kml_descr = '<p>'
#         kml_descr += 'Scientific name: ' + scientific_name + '<br>'
#         kml_descr += 'Latitude: ' + latitude + '<br>'
#         kml_descr += 'Longitude: ' + longitude + '<br>'
#         kml_descr += '</p>'
#         #
#         row_dict = {}
#         row_dict['kml_name'] = scientific_name
#         row_dict['kml_description'] = kml_descr
#         row_dict['kml_kml'] = taxon_pos_dict[key] # Geographic point in KML format.
#         kml_data.append(row_dict)
#         
#     return render_to_kml("positions_kml.kml", {'kml_name' : kml_name,
#                                              'kml_description' : kml_description,
#                                              'kml_data' : kml_data})
 
# def yearInfoKml(request):
#     """ """
#     db_filter_dict = {}
#     url_param_list = []
#     forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
#     #
#     # Only show ACTIVE rows as a part of the KML file.
#     db_filter_dict['status__iexact'] = 'ACTIVE'
#     observations  = models.SpeciesObs.objects.kml().filter(**db_filter_dict)
#     #
#     # Extract and aggregate data.
#     year_datatype_taxon_pos_dict = {}
#     obsdict = None
#     for obs in observations:
#         year_datatype_taxon_pos_key = (obs.sampling_year, obs.data_type, obs.scientific_name, obs.longitude_dd, obs.latitude_dd)
#         if year_datatype_taxon_pos_key not in year_datatype_taxon_pos_dict:
#             obsdict = {}
#             obsdict['counter'] = 0
#             obsdict['sampling_month_set'] = set()
#             year_datatype_taxon_pos_dict[year_datatype_taxon_pos_key] = obsdict
#             
#         #
#         obsdict = year_datatype_taxon_pos_dict[year_datatype_taxon_pos_key]
#         obsdict['data_type'] = obs.data_type
#         obsdict['sampling_year'] = obs.sampling_year
#         obsdict['taxon_kingdom'] = obs.taxon_kingdom
#         obsdict['taxon_phylum'] = obs.taxon_phylum
#         obsdict['taxon_class'] = obs.taxon_class
#         obsdict['taxon_order'] = obs.taxon_order
#         obsdict['scientific_name'] = obs.scientific_name
#         obsdict['latitude_dd'] = obs.latitude_dd
#         obsdict['longitude_dd'] = obs.longitude_dd
#         obsdict['counter'] += 1
#         obsdict['sampling_month_set'].add(obs.sampling_month)
#         obsdict['kml_kml'] = obs.kml # Geographic point in KML format.
#     #
#     
#     # Reformat to match the template "species_kml.kml".
#     kml_name = 'SHARKdata: Marine species observations.'
#     kml_description = """
#         Data source: <a href="http://sharkdata.se">http://sharkdata.se</a> <br>
#     """ 
#     #
#     kml_data = []
#     last_used_year = None
#     year_dict = {}
#     for key in sorted(year_datatype_taxon_pos_dict.keys()):
#         year_taxon_pos = year_datatype_taxon_pos_dict[key]
#         data_type = year_taxon_pos['data_type']
#         year = year_taxon_pos['sampling_year']
#         taxon_kingdom = year_taxon_pos['taxon_kingdom']
#         taxon_phylum = year_taxon_pos['taxon_phylum']
#         taxon_class = year_taxon_pos['taxon_class']
#         taxon_order = year_taxon_pos['taxon_order']
#         scientific_name = year_taxon_pos['scientific_name']
#         latitude_dd = year_taxon_pos['latitude_dd']
#         longitude_dd = year_taxon_pos['longitude_dd']
#         counter = unicode(year_taxon_pos['counter'])
#         sampling_month = ', '.join(sorted(year_taxon_pos['sampling_month_set']))
#         kml_kml = year_taxon_pos['kml_kml'] # Geographic point in KML format.
#         #
#         if (last_used_year == None) or (last_used_year != year) :
#             last_used_year = year
#             year_dict = {}
#             year_dict['kml_name'] = 'Year: ' + year + ' Category: ' + data_type
#             year_dict['rows'] = []  
#             kml_data.append(year_dict)
#         #
#         row_dict = {}
#         row_dict['kml_name'] = scientific_name
#         #
#         kml_descr = '<p>'
#         if data_type:
#             kml_descr += 'Category: ' + data_type + '<br>'
#         if taxon_kingdom:
#             kml_descr += 'Kingdom: ' + taxon_kingdom + '<br>'
#         if taxon_phylum:
#             kml_descr += 'Phylum: ' + taxon_phylum + '<br>'
#         if taxon_class:
#             kml_descr += 'Class: ' + taxon_class + '<br>'
#         if taxon_order:
#             kml_descr += 'Order: ' + taxon_order + '<br>'
#         kml_descr += 'Scientific name: ' + scientific_name + '<br>'
#         kml_descr += 'Year: ' + year + '<br>'
#         kml_descr += 'Latitude: ' + latitude_dd + '<br>'
#         kml_descr += 'Longitude: ' + longitude_dd + '<br>'
#         kml_descr += 'Number of samples: ' + counter + '<br>'
#         kml_descr += 'Months observed: ' + sampling_month + '<br>'
#         kml_descr += '</p>'
#         
#         row_dict['kml_description'] = kml_descr 
#         row_dict['kml_kml'] = kml_kml 
#         year_dict['rows'].append(row_dict)
#         
#     return render_to_kml("year_info_kml.kml", {'kml_name' : kml_name,
#                                              'kml_description' : kml_description,
#                                              'kml_data' : kml_data})
 
# def mapOpenlayers(request):
#     db_filter_dict = {}
#     url_param_list = []
#     forms.parse_filter_params(request.GET, db_filter_dict, url_param_list) 
#     #
#     url_params = '' 
#     if url_param_list:
#         url_params += '?'
#         url_params += '&'.join(url_param_list)
#     kml_link = '/speciesobs/positions.kml/' + url_params
#     # Only show ACTIVE rows.
#     db_filter_dict['status__iexact'] = 'ACTIVE'
#     observations_count  = models.SpeciesObs.objects.kml().filter(**db_filter_dict).count()
#     
#     return render_to_response('speciesobs_map.html', {'kml_link' : kml_link,
#                                                       'location_count' : observations_count}) 

