#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#

import os
import json
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
import django.core.paginator as paginator
import app_datasets.models as models
import app_datasets.forms as forms
import app_datasets.dataset_utils as dataset_utils
import app_datasets.metadata_utils as metadata_utils
import app_sharkdataadmin.models as admin_models

def datasetDataText(request, dataset_name):
    """ Returns data in text format for a specific dataset. """
    #
    header_language = request.GET.get('header_language', None)
    #
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    data_as_text = dataset_utils.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '.txt')
    if header_language:
        # Extract first row and translate.
        rows = data_as_text.split(u'\r\n')
        if len(rows) > 0:
            headerrow = dataset_utils.DatasetUtils().translateDataHeaders(rows[0].split(u'\t'), 
                                                                          language = header_language)
            response.write((u'\t'.join(headerrow) + u'\r\n').encode(u'cp1252'))
        if len(rows) > 0:
            response.write(u'\r\n'.join(rows[1:]).encode(u'cp1252'))
    else:
        response.write(data_as_text.encode(u'cp1252'))
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
    data_as_text = dataset_utils.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '.json')  
    response.write(u'{')
    row_delimiter = u''
#     for index, row in enumerate(data_as_text.split(u'\r\n')):
    for index, row in enumerate(data_as_text.split(u'\n')):
        rowitems = row.strip().split(u'\t')
        if index == 0:
            response.write(u'"header": ["')
            if header_language:
                rowitems = dataset_utils.DatasetUtils().translateDataHeaders(rowitems, 
                                                                             language = header_language)
            #
            outrow = u'", "'.join(rowitems) + u'"], '
            #
            response.write(outrow.encode(u'cp1252'))
            response.write(u' "rows": [')
        else:
            if len(rowitems) > 1:
                outrow = row_delimiter + u'["' + '", "'.join(rowitems) + u'"]'
                response.write(outrow.encode(u'cp1252'))      
                row_delimiter = u', '
    response.write(u']')
    response.write(u'}')
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
    data_as_text = dataset_utils.DatasetUtils().getDataColumnsAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_COLUMNS.txt')  
    if header_language:
        # Extract first row and translate.
        rows = data_as_text.split(u'\r\n')
        if len(rows) > 0:
            headerrow = dataset_utils.DatasetUtils().translateDataHeaders(rows[0].split(u'\t'), 
                                                                          language = header_language)
            response.write((u'\t'.join(headerrow) + u'\r\n').encode(u'cp1252'))
        if len(rows) > 0:
            response.write(u'\r\n'.join(rows[1:]).encode(u'cp1252'))
    else:
        response.write(data_as_text.encode(u'cp1252'))
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
    data_as_text = dataset_utils.DatasetUtils().getDataColumnsAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=' + dataset_file_name.replace('.zip', '_COLUMNS.json')   
    response.write(u'{')
    row_delimiter = u''
#     for index, row in enumerate(data_as_text.split(u'\r\n')):
    for index, row in enumerate(data_as_text.split(u'\n')):
        rowitems = row.strip().split(u'\t')
        if index == 0:
            response.write(u'"header": ["')
            if header_language:
                rowitems = dataset_utils.DatasetUtils().translateDataHeaders(rowitems, 
                                                                             language = header_language)
            #
            outrow = u'", "'.join(rowitems) + u'"], '
            response.write(outrow.encode(u'cp1252'))
            response.write(u' "rows": [')
        else:
            if len(rowitems) > 1:
                outrow = row_delimiter + u'["' + '", "'.join(rowitems) + u'"]'
                response.write(outrow.encode(u'cp1252'))      
                row_delimiter = u', '
    response.write(u']')
    response.write(u'}')
    #
    return response

def datasetMetadataText(request, dataset_name):
    """ Returns metadata in text format for a specific dataset. """
    dataset = models.Datasets.objects.get(dataset_name = dataset_name)
    dataset_file_name = dataset.dataset_file_name
    #
    metadata_as_text = dataset_utils.DatasetUtils().getMetadataAsText(dataset_name)
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
    metadata_as_text = dataset_utils.DatasetUtils().getMetadataAsText(dataset_name)
    metadata_dict = {}
    for row in metadata_as_text.split(u'\r\n'):
        if u':' in row:
            parts = row.split(u':', 1) # Split on first occurence.
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
    metadata_as_text = dataset_utils.DatasetUtils().getMetadataAsText(dataset_name)
    #
    metadata_xml = metadata_utils.MetadataUtils().metadataToIso19139(metadata_as_text)
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
    selected_datatype = request.GET.get('datatype', u'All')
    #
    if (selected_datatype and (selected_datatype != u'All')):
        datasets = models.Datasets.objects.all().filter(datatype = selected_datatype).order_by(u'dataset_name')
    else:
        datasets = models.Datasets.objects.all().order_by(u'dataset_name')
    #
    datatypes = models.Datasets.objects.values_list(u'datatype').distinct().order_by(u'datatype')
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
                              {u'row_info' : row_info, 
                               u'page' : pagination_page,
                               u'per_page' : pagination_size,
                               u'prev_page' :  prev_page,
                               u'next_page' : next_page,
                               u'pages' : pag.num_pages,
                               u'datatypes' : datatype_list,
                               u'selected_datatype' : selected_datatype,
                               u'datasets' : datasets_page})
    
def listDatasetsJson(request):
    """ Generates a JSON file containing a list of datasets and their properties. """
    data_header = dataset_utils.DatasetUtils().getDatasetListHeaders()
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
    data_header = dataset_utils.DatasetUtils().getDatasetListHeaders()
    translated_header = dataset_utils.DatasetUtils().translateDatasetListHeaders(data_header, 
                                                                                 language = header_language)
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response['Content-Disposition'] = 'attachment; filename=sharkdata_datasets.txt'    
    response.write(u'\t'.join(translated_header) + u'\r\n') # Tab separated.
    for row in data_rows:
        response.write(u'\t'.join(map(unicode, row)) + u'\r\n') # Tab separated.        
    return response

def tableDatasetsJson(request):
    """ Generates a text file containing a list of datasets and their properties. 
        Organised as header and rows.
    """
    data_header = dataset_utils.DatasetUtils().getDatasetListHeaders()
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'application/json; charset=cp1252')
    response['Content-Disposition'] = 'attachment; filename=sharkdata_datasets.json'    
    response.write(u'{')
    response.write(u'"header": ["')
    response.write(u'", "'.join(data_header) + u'"], ') # Tab separated.
    response.write(u'"rows": [')
    row_delimiter = u''
    for row in data_rows:
        response.write(row_delimiter + u'["' + '", "'.join(map(unicode, row)) + u'"]')      
        row_delimiter = u', '
    response.write(u']')
    response.write(u'}')
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
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == u'on'):
                    # Delete the marked dataset version. Earlier versions vill be used, if there are any. 
                    logrow_id = admin_models.createLogRow(command = u'Delete dataset (FTP)', status = u'RUNNING', user = user)
                    try:
                        error_message = dataset_utils.DatasetUtils().deleteFileFromFtp(dataset.dataset_file_name)
                        error_message = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(user)
                        admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                    except:
                        error_message = u"Can't delete dataset from the ftp."
                        admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
                else:
                    logrow_id = admin_models.createLogRow(command = u'Delete dataset (DB)', status = u'RUNNING', user = user)
                    try:
                        dataset = models.Datasets.objects.get(id=dataset_id)
                        dataset.delete()
                    except:
                        error_message = u"Can't delete dataset from the database."
                        admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
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
