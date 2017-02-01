#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import json
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template.context_processors import csrf
from django.shortcuts import render_to_response
from django.conf import settings
from  wsgiref.util import FileWrapper
import django.core.paginator as paginator
import app_datasets.models as models
import app_datasets.forms as forms
import app_sharkdataadmin.models as admin_models
import sharkdata_core

def datasetDataText(request, dataset_name):
    """ Returns data in text format for a specific dataset. """
    #
    header_language = request.GET.get('header_language', None)
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    data_as_text = sharkdata_core.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '.txt')
    if header_language:
        # Extract first row and translate.
        rows = data_as_text.split('\r\n')
        if len(rows) > 0:
            headerrow = sharkdata_core.DatasetUtils().translateDataHeaders(rows[0].split('\t'), 
                                                                          language = header_language)
            response.write(('\t'.join(headerrow) + '\r\n').encode('cp1252'))
        if len(rows) > 0:
            response.write('\r\n'.join(rows[1:]).encode('cp1252'))
    else:
        response.write(data_as_text.encode('cp1252'))
    #
    return response

def datasetDataJson(request, dataset_name):
    """ Returns data in JSON format for a specific dataset. """
    #
    header_language = request.GET.get('header_language', None)
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    data_as_text = sharkdata_core.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '.json')  
    response.write('{')
    row_delimiter = ''
#     for index, row in enumerate(data_as_text.split('\r\n')):
    for index, row in enumerate(data_as_text.split('\n')):
        rowitems = row.strip().split('\t')
        if index == 0:
            response.write('"header": ["')
            if header_language:
                rowitems = sharkdata_core.DatasetUtils().translateDataHeaders(rowitems, 
                                                                             language = header_language)
            #
            outrow = '", "'.join(rowitems) + '"], '
            #
            response.write(outrow.encode('cp1252'))
            response.write(' "rows": [')
        else:
            if len(rowitems) > 1:
                outrow = row_delimiter + '["' + '", "'.join(rowitems) + '"]'
                response.write(outrow.encode('cp1252'))      
                row_delimiter = ', '
    response.write(']')
    response.write('}')
    #
    return response

def datasetDataColumnsText(request, dataset_name):
    """ Returns data in text format for a specific dataset.
        Column format.
    """
    #
    header_language = request.GET.get('header_language', None)
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    data_as_text = sharkdata_core.DatasetUtils().getDataColumnsAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_COLUMNS.txt')  
    if header_language:
        # Extract first row and translate.
        rows = data_as_text.split('\r\n')
        if len(rows) > 0:
            headerrow = sharkdata_core.DatasetUtils().translateDataHeaders(rows[0].split('\t'), 
                                                                          language = header_language)
            response.write(('\t'.join(headerrow) + '\r\n').encode('cp1252'))
        if len(rows) > 0:
            response.write('\r\n'.join(rows[1:]).encode('cp1252'))
    else:
        response.write(data_as_text.encode('cp1252'))
    #
    return response

def datasetDataColumnsJson(request, dataset_name):
    """ Returns data in JSON format for a specific dataset. 
        Column format.
    """
    #
    header_language = request.GET.get('header_language', None)
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    data_as_text = sharkdata_core.DatasetUtils().getDataColumnsAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_COLUMNS.json')   
    response.write('{')
    row_delimiter = ''
#     for index, row in enumerate(data_as_text.split('\r\n')):
    for index, row in enumerate(data_as_text.split('\n')):
        rowitems = row.strip().split('\t')
        if index == 0:
            response.write('"header": ["')
            if header_language:
                rowitems = sharkdata_core.DatasetUtils().translateDataHeaders(rowitems, 
                                                                             language = header_language)
            #
            outrow = '", "'.join(rowitems) + '"], '
            response.write(outrow.encode('cp1252'))
            response.write(' "rows": [')
        else:
            if len(rowitems) > 1:
                outrow = row_delimiter + '["' + '", "'.join(rowitems) + '"]'
                response.write(outrow.encode('cp1252'))      
                row_delimiter = ', '
    response.write(']')
    response.write('}')
    #
    return response

def datasetMetadataText(request, dataset_name):
    """ Returns metadata in text format for a specific dataset. """
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    metadata_as_text = sharkdata_core.DatasetUtils().getMetadataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_METADATA.txt')  
    response.write(metadata_as_text)
    return response

def datasetMetadataJson(request, dataset_name):
    """ Returns metadata in JSON format for a specific dataset. """
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    metadata_as_text = sharkdata_core.DatasetUtils().getMetadataAsText(dataset_name)
    metadata_dict = {}
    for row in metadata_as_text.split('\r\n'):
        if ':' in row:
            parts = row.split(':', 1) # Split on first occurence.
            key = parts[0].strip()
            value = parts[1].strip()
            metadata_dict[key] = value
    #
    response = HttpResponse(content_type = 'application/json; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename=' +dataset_file_name.replace('.zip', '_METADATA.json')    
    response.write(json.dumps(metadata_dict, encoding = 'utf-8'))
    return response

def datasetMetadataXml(request, dataset_name):
    """ Returns metadata in XML (ISO 19139) format for a specific dataset. """
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    metadata_as_text = sharkdata_core.DatasetUtils().getMetadataAsText(dataset_name)
    #
    metadata_xml = sharkdata_core.MetadataUtils().metadataToIso19139(metadata_as_text)
    #
    response = HttpResponse(content_type = 'application/xml; charset=utf-8')    
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_METADATA.xml')    
    response.write(metadata_xml)
    return response



def sharkArchiveZip(request, dataset_name):
    """ Returns the SHARK Archive file. """
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    ftp_file_path = dataset.ftp_file_path
    #
    wrapper = FileWrapper(file(ftp_file_path))
    response = StreamingHttpResponse(wrapper, content_type = 'application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % dataset_file_name
    response['Content-Length'] = os.path.getsize(ftp_file_path)
    #
    return response
    
def dwcArchiveZip(request, dataset_name):
    """ Returns the prepared Darwin Core Arcive file. """
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    archive_file_name = os.path.basename(dataset.dwc_archive_file_path)
    archive_file_path = dataset.dwc_archive_file_path
    #
    wrapper = FileWrapper(file(archive_file_path))
    response = StreamingHttpResponse(wrapper, content_type = 'application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % archive_file_name
    response['Content-Length'] = os.path.getsize(archive_file_path)
    #
    return response

def dwcArchiveEurobisZip(request, dataset_name):
    """ Returns the prepared Darwin Core Arcive (EurOBIS format) file. """
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    archive_file_name = os.path.basename(dataset.dwc_archive_eurobis_file_path)
    archive_file_path = dataset.dwc_archive_eurobis_file_path
    #
    wrapper = FileWrapper(file(archive_file_path))
    response = StreamingHttpResponse(wrapper, content_type = 'application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % archive_file_name
    response['Content-Length'] = os.path.getsize(archive_file_path)
    #
    return response

def dwcArchiveSampledataZip(request, dataset_name):
    """ Returns the prepared Darwin Core Arcive (Sample Data format) file. """
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    archive_file_name = os.path.basename(dataset.dwc_archive_sampledata_file_path)
    archive_file_path = dataset.dwc_archive_sampledata_file_path
    #
    wrapper = FileWrapper(file(archive_file_path))
    response = StreamingHttpResponse(wrapper, content_type = 'application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s' % archive_file_name
    response['Content-Length'] = os.path.getsize(archive_file_path)
    #
    return response


##############################################################################################################

def listDatasets(request):
    """ Generates an HTML page listing all datasets. """

    # URL parameters.
    per_page_default = 10
    try:
        pagination_page = int(request.GET.get('page', 1))
    except:
        pagination_page = 1
    try:
        pagination_size = int(request.GET.get('per_page', per_page_default))
    except:
        pagination_size = per_page_default    
    selected_datatype = request.GET.get('datatype', 'All')
    #
    if (selected_datatype and (selected_datatype != 'All')):
        datasets = models.Datasets.objects.all().filter(datatype = selected_datatype).order_by('dataset_name')
    else:
        datasets = models.Datasets.objects.all().order_by('dataset_name')
    #
    datatypes = models.Datasets.objects.values_list('datatype').distinct().order_by('datatype')
    datatype_list = []
    for datatype in datatypes:
        try:
            datatype_list.append(datatype[0])
        except:
            pass
    #
    pag = paginator.Paginator(datasets, pagination_size)
    pagination_page = pagination_page if pagination_page <= pag.num_pages else 1
    try:
        datasets_page = pag.page(pagination_page)
    except paginator.EmptyPage:
        datasets_page = [] # If page is out of range, return empty list.
    #
    number_of_rows = len(datasets)
    first_row = (pagination_page - 1) * pagination_size + 1
    last_row = first_row + pagination_size - 1
    last_row = last_row if last_row <= number_of_rows else number_of_rows
    row_info = u"Row " + unicode(first_row) + " - " + unicode(last_row) + " of " + unicode(number_of_rows) 
    prev_page = pagination_page - 1 if pagination_page > 1 else pagination_page
    next_page = pagination_page + 1 if pagination_page < pag.num_pages else pagination_page

    return render_to_response("list_datasets.html",
                              {'row_info' : row_info, 
                               'page' : pagination_page,
                               'per_page' : pagination_size,
                               'prev_page' :  prev_page,
                               'next_page' : next_page,
                               'pages' : pag.num_pages,
                               'datatypes' : datatype_list,
                               'selected_datatype' : selected_datatype,
                               'datasets' : datasets_page})
    
def listDatasetsJson(request):
    """ Generates a JSON file containing a list of datasets and their properties. """
    data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
    datasets_json = []
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    for data_row in data_rows:
        row_dict = dict(zip(data_header, map(unicode, data_row)))
        datasets_json.append(row_dict)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=sharkdata_dataset_list.json'    
    response.write(json.dumps(datasets_json, encoding = 'utf8'))
    return response

def tableDatasetsText(request):
    """ Generates a text file containing a list of datasets and their properties. """
    header_language = request.GET.get('header_language', None)
    data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
    translated_header = sharkdata_core.DatasetUtils().translateDatasetListHeaders(data_header, 
                                                                                 language = header_language)
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response['Content-Disposition'] = 'attachment; filename=sharkdata_datasets.txt'    
    response.write('\t'.join(translated_header) + '\r\n') # Tab separated.
    for row in data_rows:
        response.write('\t'.join(map(unicode, row)) + '\r\n') # Tab separated.        
    return response

def tableDatasetsJson(request):
    """ Generates a text file containing a list of datasets and their properties. 
        Organised as header and rows.
    """
    data_header = sharkdata_core.DatasetUtils().getDatasetListHeaders()
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=sharkdata_datasets.json'    
    response.write('{')
    response.write('"header": ["')
    response.write('", "'.join(data_header) + '"], ') # Tab separated.
    response.write('"rows": [')
    row_delimiter = ''
    for row in data_rows:
        response.write(row_delimiter + '["' + '", "'.join(map(unicode, row)) + '"]')      
        row_delimiter = ', '
    response.write(']')
    response.write('}')
    #
    return response

def deleteDataset(request, dataset_id):
    """ Deletes one row in the database. """
    dataset = models.Datasets.objects.get(id=dataset_id)
    #
    if request.method == "GET":
        form = forms.DeleteDatasetForm()
        contextinstance = {'form'   : form,
                           'dataset' : dataset,
                           'error_message' : None}
        contextinstance.update(csrf(request))
        return render_to_response("delete_dataset.html", contextinstance)
    elif request.method == "POST":
        error_message = None # initially.
        #
        form = forms.DeleteDatasetForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == 'on'):
                    # Delete the marked dataset version. Earlier versions vill be used, if there are any. 
                    logrow_id = admin_models.createLogRow(command = 'Delete dataset (FTP)', status = 'RUNNING', user = user)
                    try:
                        error_message = sharkdata_core.DatasetUtils().deleteFileFromFtp(dataset.dataset_file_name)
                        error_message = sharkdata_core.DatasetUtils().writeLatestDatasetsInfoToDb(user)
                        admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                    except:
                        error_message = u"Can't delete dataset from the ftp."
                        admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
                else:
                    logrow_id = admin_models.createLogRow(command = 'Delete dataset (DB)', status = 'RUNNING', user = user)
                    try:
                        dataset = models.Datasets.objects.get(id=dataset_id)
                        dataset.delete()
                    except:
                        error_message = u"Can't delete dataset from the database."
                        admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/datasets")
        #
        contextinstance = {'form'   : form,
                           'dataset' : dataset,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("delete_dataset.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/datasets")
