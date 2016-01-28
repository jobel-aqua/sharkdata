#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django import forms

# class ImportDatasetForm(forms.Form):
#     """ """
#     import_file = forms.FileField(label="Select a SHARK archive file")
#     user = forms.CharField(label="User")
#     password = forms.CharField(label="Password", widget=forms.PasswordInput())

class DeleteDatasetForm(forms.Form):
    """ """
    delete_ftp = forms.BooleanField(label='Remove from FTP', required = False, initial = False)
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

# class DeleteAllDatasetsForm(forms.Form):
#     """ """
#     delete_ftp = forms.BooleanField(label='Remove from FTP', required = False, initial = False)
#     user = forms.CharField(label="User")
#     password = forms.CharField(label="Password", widget=forms.PasswordInput())
# 
# class LoadAllDatasetsForm(forms.Form):
#     """ """
#     update_metadata = forms.BooleanField(label='Update metadata', required = False, initial = False)
#     user = forms.CharField(label="User")
#     password = forms.CharField(label="Password", widget=forms.PasswordInput())

