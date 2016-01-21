#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
import app_resources.models as models
import app_resources.forms as forms
import app_resources.resources_utils as resources_utils

def resourceContentText(request, resource_name):
    """ Returns data in text format for a specific resource. """
    resource = models.Resources.objects.get(resource_name = resource_name)
    data_as_text = resource.file_content
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(data_as_text.encode(u'cp1252'))
    return response

def listResources(request):
    """ Generates an HTML page listing all resources. """
    resources = models.Resources.objects.all().order_by(u'resource_name')
    #
    return render_to_response("list_resources.html",
                              {'resources' : resources})

def listResourcesJson(request):
    """ Generates a JSON file containing a list of resources and their properties. """
    data_header = resources_utils.ResourcesUtils().getHeaders()
    resources_json = []
    #
    data_rows = models.Resources.objects.values_list(*data_header)
    for data_row in data_rows:
        row_dict = dict(zip(data_header, data_row))
        resources_json.append(row_dict)
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(json.dumps(resources_json, encoding = 'utf8'))
    return response
    
def tableResourcesText(request):
    """ Generates a text file containing a list of resources and their properties. """
    data_header = resources_utils.ResourcesUtils().getHeaders()
    translated_header = resources_utils.ResourcesUtils().translateHeaders(data_header)
    #
    data_rows = models.Resources.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'text/plain')    
    response.write(u'\t'.join(translated_header) + u'\r\n') # Tab separated.
    for row in data_rows:
        response.write(u'\t'.join(row) + u'\r\n') # Tab separated.        
    return response

def tableResourcesJson(request):
    """ Generates a text file containing a list of resources and their properties. 
        Organised as header and rows.
    """
    data_header = resources_utils.ResourcesUtils().getHeaders()
    #
    data_rows = models.Resources.objects.values_list(*data_header)
    #
    response = HttpResponse(content_type = 'application/json')
    response.write(u'{')
    response.write(u'"header": ["')
    response.write(u'", "'.join(data_header) + u'"], ') # Tab separated.
    response.write(u"'rows': [")
    row_delimiter = u''
    for row in data_rows:
        response.write(row_delimiter + u'["' + '", "'.join(row) + u'"]')      
        row_delimiter = u', '
    response.write(u']')
    response.write(u'}')
    #
    return response

def importResource(request):
    """ Used for uploading of resources. """
    
    if request.method == "GET":
        # Activates info page for uploading.
        form = forms.ImportResourceForm()
        return render_to_response("import_resource.html",
                                  {'form'   : form,
                                   'error_message' : None})
    elif request.method == "POST":
        # Reloads db-stored data.
        resources_utils.ResourcesUtils().clear()
        # Performs the uploading.
        error_message = None # initially.
        #
        form = forms.ImportResourceForm(request.POST, request.FILES)
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
                    resources_utils.ResourcesUtils().saveUploadedFileToFtp(uploaded_file)
                except:
                    error_message = u"Can't save file to the FTP area."
            #
            if error_message == None:
                try:
                    resources_utils.ResourcesUtils().writeResourcesInfoToDb(user)
                except:
                    error_message = u"Can't save this to the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/resources")
        #
        return render_to_response("import_resource.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/resources")

def deleteResources(request):
    """ Deletes all rows in the database. The FTP area is not affected. """
    if request.method == "GET":
        #
        form = forms.DeleteAllResourcesForm()
        return render_to_response("delete_all_resources.html",
                                  {'form'   : form,
                                   'error_message' : None})
    elif request.method == "POST":
        # Reloads db-stored data.
        resources_utils.ResourcesUtils().clear()
        #
        error_message = None # initially.
        #
        form = forms.DeleteAllResourcesForm(request.POST)
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
                        resources_utils.ResourcesUtils().deleteAllFilesFromFtp()
                    except:
                        error_message = u"Can't delete resources from the database."
            #
            if error_message == None:
                try:
                    models.Resources.objects.all().delete()
                except:
                    error_message = u"Can't delete resources from the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/resources")
        #
        return render_to_response("delete_all_resources.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/resources")

def deleteResource(request, resource_id):
    """ Deletes one row in the database. The FTP area is not affected. """
    resource = models.Resources.objects.get(id=resource_id)
    #
    if request.method == "GET":
        form = forms.DeleteResourceForm()
        return render_to_response("delete_resource.html",
                                  {'form'   : form,
                                   'resource' : resource,
                                   'error_message' : None})
    elif request.method == "POST":
        # Reloads db-stored data.
        resources_utils.ResourcesUtils().clear()
        #
        error_message = None # initially.
        #
        form = forms.DeleteResourceForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            if user not in settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.keys():
                error_message = u'Not a valid user. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == u'on'):
                    try:
                        resources_utils.ResourcesUtils().deleteFileFromFtp(resource.resource_file_name)
                    except:
                        error_message = u"Can't delete resources from the database."
            #
            if error_message == None:
                try:
                    resource = models.Resources.objects.get(id=resource_id)
                    resource.delete()
                except:
                    error_message = u"Can't delete resource from the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/resources")
        #
        return render_to_response("delete_resource.html",
                                  {'form'   : form,
                                   'resource' : resource,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/resources")
    
def loadAllResources(request):
    """ Updates the database from resources stored in the FTP area.
    """
    if request.method == "GET":
        form = forms.LoadAllResourcesForm()
        return render_to_response("load_all_resources.html",
                                  {'form'   : form})
    elif request.method == "POST":
        # Reloads db-stored data.
        resources_utils.ResourcesUtils().clear()
        #
        error_message = None # initially.
        #
        form = forms.LoadAllResourcesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
#                try:
                resources_utils.ResourcesUtils().writeResourcesInfoToDb(user)
#                except:
#                    error_message = u"Can't load resources and save to the database."
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/resources")
        #
        return render_to_response("load_all_resources.html",
                                  {'form'   : form,
                                   'error_message' : error_message})
    # Not a valid request method.
    return HttpResponseRedirect("/resources")
    
    
