#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

def viewDocumentation(request):
    """ """    
    return render_to_response("documentation.html")

def viewDataPolicy(request):
    """ """    
    return render_to_response("datapolicy.html")

def viewAbout(request):
    """ """    
    return render_to_response("about.html")

