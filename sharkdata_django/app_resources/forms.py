#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django import forms

CHARACTER_ENCODINGS = [("windows-1252",  "Windows-1252"),
                       ("ascii",  "ASCII"),
                       ("latin-1", "Latin-1"),
                       ("utf-8",   "UTF-8")]

RESOURCE_TYPES = [('unspecified', 'Unspecified'),
                  ('settings', 'Settings'),
                  ('vocabular', 'Vocabular'),
                  ('species_list', 'Species list')]

class ImportResourceForm(forms.Form):
    """ """
    import_file = forms.FileField(label="Select a resource file")
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class DeleteResourceForm(forms.Form):
    """ """
    delete_ftp = forms.BooleanField(label='Remove from FTP', required = False, initial = False)
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class DeleteAllResourcesForm(forms.Form):
    """ """
    delete_ftp = forms.BooleanField(label='Remove from FTP', required = False, initial = False)
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class LoadAllResourcesForm(forms.Form):
    """ """
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

