#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#

# import json
from django.http import HttpResponse,HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
# import django.core.paginator as paginator
from django.conf import settings

import app_sharkdataadmin.forms as forms
import app_sharkdataadmin.models as admin_models
import app_datasets.models as datasets_models
import app_resources.models as resources_models
import app_speciesobs.models as speciesobs_models
import app_datasets.dataset_utils as dataset_utils
import app_resources.resources_utils as resources_utils
import app_speciesobs.speciesobs_utils as speciesobs_utils

def sharkDataAdmin(request):
    """ """
    log_rows_per_page = 5
    try:
        if 'log_rows_per_page' in request.GET:
            log_rows_per_page = int(request.GET['log_rows_per_page'])
    except:
        pass
    
    logrows = admin_models.CommandLog.objects.all().order_by('-id')[:log_rows_per_page] # Reverse order.
    #
    return render_to_response("sharkdata_admin.html",
                              {'logrows' : logrows})

def viewLog(request, log_id):
    """ """
    command_log = admin_models.CommandLog.objects.get(id=log_id)
    result_log = command_log.result_log
    #
    response = HttpResponse(content_type = 'text/plain; charset=cp1252')    
    response.write(result_log.encode(u'cp1252'))
    return response


# def importDataset(request):
#     """ Used for uploading of datasets. """
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         # Activates info page for uploading.
#         form = forms.ImportDatasetForm()
#         contextinstance = {'form'   : form,
#                            'error_message' : error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("datasets_import.html", contextinstance)
#     elif request.method == "POST":
#         # Performs the uploading.
#         error_message = None # initially.
#         #
#         form = forms.ImportDatasetForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['import_file']
#             #
#             user = request.POST['user']
#             password = request.POST['password']
#             if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
#                 error_message = u'Not a valid user or password. Please try again...'   
#             #
#             if error_message == None:
#                 logrow_id = admin_models.createLogRow(command = u'Import dataset (FTP)', status = u'RUNNING', user = user)
#                 try:
#                     # Save uploaded file to FTP area.
#                     error_message = dataset_utils.DatasetUtils().saveUploadedFileToFtp(uploaded_file)
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
#                 except:
#                     error_message = u"Can't save file to the FTP area." 
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#             #
#             if error_message == None:
#                 logrow_id = admin_models.createLogRow(command = u'Import dataset (DB)', status = u'RUNNING', user = user)
#                 try:
#                     # Add info to database.
#                     error_message = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(user)
#                 except:
#                     error_message = u"Can't save this to the database."
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/sharkdataadmin")
#         #
#         contextinstance = {'form'   : form,
#                            'error_message' : error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("datasets_import.html", contextinstance)
#     # Not a valid request method.
#     return HttpResponseRedirect("/sharkdataadmin")

def deleteDatasets(request):
    """ Deletes all rows in the database. """
    error_message = None # initially.
    #
    if request.method == "GET":
        #
        form = forms.DeleteAllDatasetsForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_delete_all.html", contextinstance)
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
                    logrow_id = admin_models.createLogRow(command = u'Delete all datasets from FTP', status = u'RUNNING', user = user)
                    try:
                        error_message = dataset_utils.DatasetUtils().deleteAllFilesFromFtp()
                        admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                    except:
                        error_message = u"Can't delete datasets from the FTP area."
                        admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = u'Delete all datasets from DB', status = u'RUNNING', user = user)
                try:
                    datasets_models.Datasets.objects.all().delete()
                    admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except:
                    error_message = u"Can't delete datasets from the database."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_delete_all.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def loadAllDatasets(request):
    """ Updates the database from datasets stored in the FTP area.
        I multiple versions of a dataset are in the FTP area only the latest 
        will be loaded.
    """
    error_message = None # initially.
    #
    if request.method == "GET":
        form = forms.LoadAllDatasetsForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_load_all.html", contextinstance)
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
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = u'Load all datasets from FTP to DB', status = u'RUNNING', user = user)
                try:
                    error_counter = dataset_utils.DatasetUtils().writeLatestDatasetsInfoToDb(logrow_id, user)
                    if error_counter > 0:
                        admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED (Errors: ' + unicode(error_counter) + u')')
                    else:
                        admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except Exception as e:
                    error_message = u"Can't load datasets and save to the database."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    if settings.DEBUG: print(u'\nError: ' + error_message + u'\nException: ' + unicode(e) + u'\n')
                    settings.LOGGER.error(u'\nError: ' + error_message + u'\nException: ' + unicode(e) + u'\n')                    
            #
#             if error_message == None:
#                 if ('update_metadata' in request.POST) and (request.POST['update_metadata'] == u'on'):
#                     dataset_utils.DatasetUtils().updateMetadataForAllDatasetsInThread(user)
            #
#             if error_message == None:
#                 if ('generate_archives' in request.POST) and (request.POST['generate_archives'] == u'on'):
#                     dataset_utils.DatasetUtils().generateArchivesForAllDatasetsInThread(user)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_load_all.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def generateArchives(request):
    """ Generates archive files (DwC-A) for all datasets.
    """
    error_message = None # initially.
    #
    if request.method == "GET":
        form = forms.GenerateArchivesForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("generate_archives.html", contextinstance)
    elif request.method == "POST":
        error_message = None # initially.
        #
        form = forms.GenerateArchivesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                    dataset_utils.DatasetUtils().generateArchivesForAllDatasetsInThread(user)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("generate_archives.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

# def importResource(request):
#     """ Used for uploading of resources. """
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         # Activates info page for uploading.
#         form = forms.ImportResourceForm()
#         contextinstance = {'form'   : form,
#                            'error_message' : error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("resources_import.html", contextinstance)
#     elif request.method == "POST":
#         # Reloads db-stored data.
#         resources_utils.ResourcesUtils().clear()
#         # Performs the uploading.
#         error_message = None # initially.
#         #
#         form = forms.ImportResourceForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['import_file']
#             #
#             user = request.POST['user']
#             password = request.POST['password']
#             if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
#                 error_message = u'Not a valid user or password. Please try again...'   
#             #
#             if error_message == None:
#                 logrow_id = admin_models.createLogRow(command = u'Import resource (FTP)', status = u'RUNNING', user = user)
#                 try:
#                     # Save uploaded file to FTP area.
#                     resources_utils.ResourcesUtils().saveUploadedFileToFtp(uploaded_file)
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
#                 except:
#                     error_message = u"Can't save file to the FTP area."
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#             #
#             if error_message == None:
#                 logrow_id = admin_models.createLogRow(command = u'Import resource (DB)', status = u'RUNNING', user = user)
#                 try:
#                     resources_utils.ResourcesUtils().writeResourcesInfoToDb(user)
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
#                 except:
#                     error_message = u"Can't save this to the database."
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/sharkdataadmin")
#         #
#         contextinstance = {'form'   : form,
#                            'error_message' : error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("resources_import.html", contextinstance)
#     # Not a valid request method.
#     return HttpResponseRedirect("/sharkdataadmin")

def deleteResources(request):
    """ Deletes all rows in the database. The FTP area is not affected. """
    error_message = None # initially.
    #
    if request.method == "GET":
        #
        form = forms.DeleteAllResourcesForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("resources_delete_all.html", contextinstance)
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
                    logrow_id = admin_models.createLogRow(command = u'Delete all resources (FTP)', status = u'RUNNING', user = user)
                    try:
                        resources_utils.ResourcesUtils().deleteAllFilesFromFtp()
                        admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                    except:
                        error_message = u"Can't delete resources from the database."
                        admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = u'Delete all resources (DB)', status = u'RUNNING', user = user)
                try:
                    resources_models.Resources.objects.all().delete()
                    admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except:
                    error_message = u"Can't delete resources from the database."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("resources_delete_all.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def loadAllResources(request):
    """ Updates the database from resources stored in the FTP area.
    """
    error_message = None # initially.
    #
    if request.method == "GET":
        form = forms.LoadAllResourcesForm()
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("resources_load_all.html", contextinstance)
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
                logrow_id = admin_models.createLogRow(command = u'Load all resources from FTP to DB', status = u'RUNNING', user = user)
                try:
                    resources_utils.ResourcesUtils().writeResourcesInfoToDb(user)
                    admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except:
                    error_message = u"Can't load resources and save to the database."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("resources_load_all.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def updateSpeciesObs(request):
    """ Updates species observations based of content in the datasets. """
    error_message = None # initially.
    #
    if request.method == "GET":
        #
        form = forms.UpdateSpeciesObsForm()
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("speciesobs_update.html", contextinstance)
    elif request.method == "POST":
        form = forms.UpdateSpeciesObsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = u'Update species observations', status = u'RUNNING', user = user)
                try:
                    error_message = speciesobs_utils.SpeciesObsUtils().updateSpeciesObsInThread(logrow_id)
                    # admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except:
                    error_message = u"Can't update species observations from datasets."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("speciesobs_update.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

# def loadSpeciesObs(request):
#     """ Load species observations from file. """
#     error_message = None # initially.
#     #
#     if request.method == "GET":
#         #
#         form = forms.LoadSpeciesObsForm()
#         contextinstance = {'form': form,
#                            'error_message': error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("speciesobs_load.html", contextinstance)
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
#                 logrow_id = admin_models.createLogRow(command = u'Load species observations from backup file', status = u'RUNNING', user = user)
#                 try:
#                     error_message = speciesobs_utils.SpeciesObsUtils().loadSpeciesObsInThread(logrow_id)
#                     # admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
#                 except:
#                     error_message = u"Can't load species observations from file."
#                     admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
#                     admin_models.addResultLog(logrow_id, result_log = error_message)
#             # OK.
#             if error_message == None:
#                 return HttpResponseRedirect("/sharkdataadmin")
#         #
#         contextinstance = {'form': form,
#                            'error_message': error_message}
#         contextinstance.update(csrf(request))
#         return render_to_response("speciesobs_load.html", contextinstance)
#     # Not a valid request method.
#     return HttpResponseRedirect("/sharkdataadmin")

def cleanUpSpeciesObs(request):
    """ Removes species observations with status='DELETED'. """
    error_message = None # initially.
    #
    if request.method == "GET":
        #
        form = forms.CleanUpSpeciesObsForm()
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("speciesobs_cleanup.html", contextinstance)
    elif request.method == "POST":
        form = forms.CleanUpSpeciesObsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = u'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = u'Clean up species observations', status = u'RUNNING', user = user)
                try:
                    error_message = speciesobs_utils.SpeciesObsUtils().cleanUpSpeciesObsInThread(logrow_id)
                    # admin_models.changeLogRowStatus(logrow_id, status = u'FINISHED')
                except:
                    error_message = u"Can't clean up species observations."
                    admin_models.changeLogRowStatus(logrow_id, status = u'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("speciesobs_cleanup.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")


    