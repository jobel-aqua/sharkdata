#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#

import json
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
import app_datasets.models as models
import app_datasets.forms as forms
import app_datasets.dataset_utils as dataset_utils

def datasetDataText(request, dataset_name):
    """ Returns data in text format for a specific dataset. """
    data_as_text = dataset_utils.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(data_as_text.encode(u'cp1252'))
    return response

def datasetDataJson(request, dataset_name):
    """ Returns data in JSON format for a specific dataset. """
    data_as_text = dataset_utils.DatasetUtils().getDataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(u'{')
    row_delimiter = u''
#     for index, row in enumerate(data_as_text.split(u'\r\n')):
    for index, row in enumerate(data_as_text.split(u'\n')):
        rowitems = row.strip().split(u'\t')
        if index == 0:
            response.write(u'"header": ["')
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
    metadata_as_text = dataset_utils.DatasetUtils().getMetadataAsText(dataset_name)
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(metadata_as_text)
    return response

def datasetMetadataJson(request, dataset_name):
    """ Returns metadata in JSON format for a specific dataset. """
    metadata_as_text = dataset_utils.DatasetUtils().getMetadataAsText(dataset_name)
    metadata_dict = {}
    for row in metadata_as_text.split(u'\r\n'):
        if u':' in row:
            parts = row.split(u':', 1) # Split on first occurence.
            key = parts[0].strip()
            value = parts[1].strip()
            metadata_dict[key] = value
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(json.dumps(metadata_dict, encoding = 'utf8'))
    return response

def datasetMetadataXml(request, dataset_name):
    """ Returns metadata in XML format for a specific dataset. """
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(u'<xml>' + u'\r\n' + u'TEST: ' + dataset_name + u'\r\n' + u'</xml>') # DUMMY for TEST.
    return response


##############################################################################################################
##############################################################################################################
##############################################################################################################

def listDatasets(request):
    """ Generates an HTML page listing all datasets. """
    datasets = models.Datasets.objects.all().order_by(u'dataset_name')
    #
    return render_to_response("list_datasets.html",
                              {'datasets' : datasets})
    
def listDatasetsJson(request):
    """ Generates a JSON file containing a list of datasets and their properties. """
    data_header = dataset_utils.DatasetUtils().getHeaders()
    datasets_json = []
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    for data_row in data_rows:
        row_dict = dict(zip(data_header, data_row))
        datasets_json.append(row_dict)
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(json.dumps(datasets_json, encoding = 'utf8'))
    return response

def tableDatasetsText(request):
    """ Generates a text file containing a list of datasets and their properties. """
    data_header = dataset_utils.DatasetUtils().getHeaders()
    translated_header = dataset_utils.DatasetUtils().translateHeaders(data_header)
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(u'\t'.join(translated_header) + u'\r\n') # Tab separated.
    for row in data_rows:
        response.write(u'\t'.join(row) + u'\r\n') # Tab separated.        
    return response

def tableDatasetsJson(request):
    """ Generates a text file containing a list of datasets and their properties. 
        Organised as header and rows.
    """
    data_header = dataset_utils.DatasetUtils().getHeaders()
    #
    data_rows = models.Datasets.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(u'{')
    response.write(u'"header": ["')
    response.write(u'", "'.join(data_header) + u'"], ') # Tab separated.
    response.write(u'"rows": [')
    row_delimiter = u''
    for row in data_rows:
        response.write(row_delimiter + u'["' + '", "'.join(row) + u'"]')      
        row_delimiter = u', '
    response.write(u']')
    response.write(u'}')
    #
    return response

def importDataset(request):
    """ Used for uploading of datasets. """
    if request.method == "GET":
        # Activates info page for uploading.
        form = forms.ImportDatasetForm()
        return render_to_response("import_dataset.html",
                                  {'form'   : form,
                                   'error_message' : None})
    elif request.method == "POST":
        # Performs the uploading.
        error_message = None # initially.
        #
        form = forms.ImportDatasetForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['import_file']
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                try:
                    # Save uploaded file to FTP area.
                    error_message = dataset_utils.DatasetUtils().saveUploadedFileToFtp(uploaded_file)
                except:
                    error_message = u"Can't save file to the FTP area." 
            #
            if error_message == None:
                try:
                    # Add info to database.
                    error_message = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(user)
                except:
                    error_message = u"Can't save this to the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/datasets")
        #
        return render_to_response("import_dataset.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/datasets")

def deleteDatasets(request):
    """ Deletes all rows in the database. """
    if request.method == "GET":
        #
        form = forms.DeleteAllDatasetsForm()
        return render_to_response("delete_all_datasets.html",
                                  {'form'   : form,
                                   'error_message' : None})
    elif request.method == "POST":
        error_message = None # initially.
        #
        form = forms.DeleteAllDatasetsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == u'on'):
                    try:
                        error_message = dataset_utils.DatasetUtils().deleteAllFilesFromFtp()
                    except:
                        error_message = u"Can't delete resources from the database."
            #
            if error_message == None:
                try:
                    models.Datasets.objects.all().delete()
                except:
                    error_message = u"Can't delete datasets from the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/datasets")
        #
        return render_to_response("delete_all_datasets.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/datasets")

def deleteDataset(request, dataset_id):
    """ Deletes one row in the database. """
    dataset = models.Datasets.objects.get(id=dataset_id)
    #
    if request.method == "GET":
        form = forms.DeleteDatasetForm()
        return render_to_response("delete_dataset.html",
                                  {'form'   : form,
                                   'dataset' : dataset,
                                   'error_message' : None})
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
                    try:
                        error_message = dataset_utils.DatasetUtils().deleteFileFromFtp(dataset.dataset_file_name)
                        error_message = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(user)
                    except:
                        error_message = u"Can't delete dataset from the ftp."
                else:
                    try:
                        dataset = models.Datasets.objects.get(id=dataset_id)
                        dataset.delete()
                    except:
                        error_message = u"Can't delete dataset from the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/datasets")
        #
        return render_to_response("delete_dataset.html",
                                  {'form'   : form,
                                   'dataset' : dataset,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/datasets")
    
def loadAllDatasets(request):
    """ Updates the database from datasets stored in the FTP area.
        I multiple versions of a dataset are in the FTP area only the latest 
        will be loaded.
    """
    if request.method == "GET":
        form = forms.LoadAllDatasetsForm()
        return render_to_response("load_all_datasets.html",
                                  {'form'   : form})
    elif request.method == "POST":
        error_message = None # initially.
        #
        form = forms.LoadAllDatasetsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            #
            if error_message == None:
                if ('update_metadata' in request.POST) and (request.POST['update_metadata'] == u'on'):
                    try:
                        # Note: This message will call writeLatestDatasetsInfoToDb() when finished.
                        error_message = dataset_utils.DatasetUtils().updateMetadataForAllDatasetsInThread()
                    except:
                        error_message = u"Can't update metadata."
            #
            if error_message == None:
                try:
                    error_message = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(user)
                except:
                    error_message = u"Can't load datasets and save to the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/datasets")
        #
        return render_to_response("load_all_datasets.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/datasets")
