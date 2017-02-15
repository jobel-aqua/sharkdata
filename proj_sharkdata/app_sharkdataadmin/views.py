#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

# import json
from django.http import HttpResponse,HttpResponseRedirect
from django.template.context_processors import csrf
from django.shortcuts import render_to_response
# import django.core.paginator as paginator
from django.conf import settings

from app_sharkdataadmin import forms
import app_sharkdataadmin.models as admin_models
import app_datasets.models as datasets_models
import app_resources.models as resources_models
import app_exportformats.models as exportformats_models
import sharkdata_core

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
    response.write(result_log.encode('cp1252'))
    return response

def deleteDatasets(request):
    """ Deletes all rows in the database. """
    error_message = None
    #
    if request.method == "GET":
        #
        form = forms.DeleteAllDatasetsForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_delete_all.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.DeleteAllDatasetsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == 'on'):
                    logrow_id = admin_models.createLogRow(command = 'Delete all datasets from FTP', status = 'RUNNING', user = user)
                    try:
                        error_message = sharkdata_core.DatasetUtils().deleteAllFilesFromFtp()
                        admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                    except:
                        error_message = u"Can't delete datasets from the FTP area."
                        admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Delete all datasets from DB', status = 'RUNNING', user = user)
                try:
                    datasets_models.Datasets.objects.all().delete()
                    admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't delete datasets from the database."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
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
    error_message = None
    #
    if request.method == "GET":
        form = forms.LoadAllDatasetsForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("datasets_load_all.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.LoadAllDatasetsForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            # Load datasets.
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Load all datasets from FTP to DB', status = 'RUNNING', user = user)
                try:
                    error_counter = sharkdata_core.DatasetUtils().writeLatestDatasetsInfoToDb(logrow_id, user)
                    if error_counter > 0:
                        admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED (Errors: ' + unicode(error_counter) + ')')
                    else:
                        admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except Exception as e:
                    error_message = u"Can't load datasets and save to the database."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
                    if settings.DEBUG: print('\nError: ' + error_message + '\nException: ' + unicode(e) + '\n')
                    settings.LOGGER.error('\nError: ' + error_message + '\nException: ' + unicode(e) + '\n')                    
            # Delete old versions of dataset files.
            if error_message == None:
                if ('delete_old_ftp_versions' in request.POST) and (request.POST['delete_old_ftp_versions'] == 'on'):
                    try:
                        error_counter = sharkdata_core.DatasetUtils().deleteOldFtpVersions(logrow_id, user)
                        if error_counter > 0:
                            admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED (Errors: ' + unicode(error_counter) + ')')
                        else:
                            admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                    except Exception as e:
                        error_message = u"Can't delete old versions in the FTP area."
                        admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
                        if settings.DEBUG: print('\nError: ' + error_message + '\nException: ' + unicode(e) + '\n')
                        settings.LOGGER.error('\nError: ' + error_message + '\nException: ' + unicode(e) + '\n')                    
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
    error_message = None
    #
    if request.method == "GET":
        form = forms.GenerateArchivesForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("generate_archives.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.GenerateArchivesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                    sharkdata_core.SharkdataAdminUtils().generateArchivesForAllDatasetsInThread(user)
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

def deleteExportFiles(request):
    """ Deletes rows in the database. """
    error_message = None
    #
    if request.method == "GET":
        #
        form = forms.DeleteExportFilesForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("exportfiles_delete_all.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.DeleteExportFilesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
#             if error_message == None:
#                 if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == 'on'):
#                     logrow_id = admin_models.createLogRow(command = 'Delete all datasets from FTP', status = 'RUNNING', user = user)
#                     try:
#                         error_message = dataset_utils.DatasetUtils().deleteAllFilesFromFtp()
#                         admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
#                     except:
#                         error_message = u"Can't delete datasets from the FTP area."
#                         admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
#                         admin_models.addResultLog(logrow_id, result_log = error_message)
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Delete all ICES-XML files from DB', status = 'RUNNING', user = user)
                try:
                    exportformats_models.ExportFiles.objects.all().delete()
                    admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't delete datasets from the database."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                    admin_models.addResultLog(logrow_id, result_log = error_message)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("exportfiles_delete_all.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def generateIcesXml(request):
    """ Generates ICES-XML file. """
    error_message = None
    #
    if request.method == "GET":
        form = forms.GenerateIcesXmlForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("generate_ices_xml.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.GenerateIcesXmlForm(request.POST)
        if form.is_valid():
            #
            datatype_list = []
            year_from = request.POST['year_from']
            year_to = request.POST['year_to']
            status = request.POST['status']
            user = request.POST['user']
            password = request.POST['password']
            #
            if ('phytobenthos' in request.POST) and (request.POST['phytobenthos'] == 'on'):
                datatype_list.append('Phytobenthos')
            if ('phytoplankton' in request.POST) and (request.POST['phytoplankton'] == 'on'):
                datatype_list.append('Phytoplankton')
            if ('zoobenthos' in request.POST) and (request.POST['zoobenthos'] == 'on'):
                datatype_list.append('Zoobenthos')
            if ('zooplankton' in request.POST) and (request.POST['zooplankton'] == 'on'):
                datatype_list.append('Zooplankton')
            #
            if ('Phytobenthos' in datatype_list) or \
               ('Phytoplankton' in datatype_list) or \
               ('Zooplankton' in datatype_list):
                error_message = 'Support for Zoobenthos only, others are under development. Please try again...'   
            #
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                    sharkdata_core.SharkdataAdminUtils().generateIcesXmlInThread(
                                                    datatype_list, year_from, year_to, status, user)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("generate_ices_xml.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def validateIcesXml(request):
    """ Validate ICES-XML file. """
    error_message = None
    #
    if request.method == "GET":
        form = forms.ValidateIcesXmlForm()
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("validate_ices_xml.html", contextinstance)
    elif request.method == "POST":
        #
        form = forms.ValidateIcesXmlForm(request.POST)
        if form.is_valid():
            #
            datatype_list = []
            user = request.POST['user']
            password = request.POST['password']
            #
            if ('phytobenthos' in request.POST) and (request.POST['phytobenthos'] == 'on'):
                datatype_list.append('Phytobenthos')
            if ('phytoplankton' in request.POST) and (request.POST['phytoplankton'] == 'on'):
                datatype_list.append('Phytoplankton')
            if ('zoobenthos' in request.POST) and (request.POST['zoobenthos'] == 'on'):
                datatype_list.append('Zoobenthos')
            if ('zooplankton' in request.POST) and (request.POST['zooplankton'] == 'on'):
                datatype_list.append('Zooplankton')
            #
            if ('Phytobenthos' in datatype_list) or \
               ('Phytoplankton' in datatype_list) or \
               ('Zooplankton' in datatype_list):
                error_message = 'Support for Zoobenthos only, others are under development. Please try again...'   
            #
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                    sharkdata_core.SharkdataAdminUtils().validateIcesXmlInThread(datatype_list, user)
            # OK.
            if error_message == None:
                return HttpResponseRedirect("/sharkdataadmin")
        #
        contextinstance = {'form'   : form,
                           'error_message' : error_message}
        contextinstance.update(csrf(request))
        return render_to_response("validate_ices_xml.html", contextinstance)
    # Not a valid request method.
    return HttpResponseRedirect("/sharkdataadmin")

def deleteResources(request):
    """ Deletes all rows in the database. The FTP area is not affected. """
    error_message = None
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
        sharkdata_core.ResourcesUtils().clear()
        #
        form = forms.DeleteAllResourcesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                if ('delete_ftp' in request.POST) and (request.POST['delete_ftp'] == 'on'):
                    logrow_id = admin_models.createLogRow(command = 'Delete all resources (FTP)', status = 'RUNNING', user = user)
                    try:
                        sharkdata_core.ResourcesUtils().deleteAllFilesFromFtp()
                        admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                    except:
                        error_message = u"Can't delete resources from the database."
                        admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
                        admin_models.addResultLog(logrow_id, result_log = error_message)
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Delete all resources (DB)', status = 'RUNNING', user = user)
                try:
                    resources_models.Resources.objects.all().delete()
                    admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't delete resources from the database."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
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
    error_message = None
    #
    if request.method == "GET":
        form = forms.LoadAllResourcesForm()
        contextinstance = {'form': form,
                           'error_message': error_message}
        contextinstance.update(csrf(request))
        return render_to_response("resources_load_all.html", contextinstance)
    elif request.method == "POST":
        # Reloads db-stored data.
        sharkdata_core.ResourcesUtils().clear()
        #
        form = forms.LoadAllResourcesForm(request.POST)
        if form.is_valid():
            #
            user = request.POST['user']
            password = request.POST['password']
            if password != settings.APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST.get(user, None):
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Load all resources from FTP to DB', status = 'RUNNING', user = user)
                try:
                    sharkdata_core.ResourcesUtils().writeResourcesInfoToDb(user)
                    admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't load resources and save to the database."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
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
    error_message = None
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
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Update species observations', status = 'RUNNING', user = user)
                try:
                    error_message = sharkdata_core.SharkdataAdminUtils().updateSpeciesObsInThread(logrow_id)
                    # admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't update species observations from datasets."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
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

def cleanUpSpeciesObs(request):
    """ Removes species observations with status='DELETED'. """
    error_message = None
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
                error_message = 'Not a valid user or password. Please try again...'   
            #
            if error_message == None:
                logrow_id = admin_models.createLogRow(command = 'Clean up species observations', status = 'RUNNING', user = user)
                try:
                    error_message = sharkdata_core.SharkdataAdminUtils().cleanUpSpeciesObsInThread(logrow_id)
                    # admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')
                except:
                    error_message = u"Can't clean up species observations."
                    admin_models.changeLogRowStatus(logrow_id, status = 'FAILED')
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


    
