#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from django import forms
import app_speciesobs.models as models

class UpdateSpeciesObsForm(forms.Form):
    """ """
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class LoadSpeciesObsForm(forms.Form):
    """ """
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class CleanUpSpeciesObsForm(forms.Form):
    """ """
    user = forms.CharField(label="User")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())


class SpeciesObsFilterForm(forms.Form):
    """ """
    def __init__(self, *args, **kwargs):
        """ Needed to update choise fields """
        super(SpeciesObsFilterForm, self).__init__(*args, **kwargs)
#         # Datasets.
#         datasets = models.SpeciesObs.objects.values_list(u'dataset_name', flat = True).distinct().order_by(u'dataset_name')   
#         dataset_choises = [('All', 'All')] + [(item, item) for item in datasets]          
#         self.fields['dataset'] = forms.ChoiceField(
#                                         choices=dataset_choises, 
#                                         required = False,
#                                         widget=forms.Select())
        # Years.
        years = models.SpeciesObs.objects.values_list(u'sampling_year', flat = True).distinct().order_by(u'sampling_year')
        year_choises = [('All', 'All')] + [(item, item) for item in years]
        self.fields['year_from'] = forms.ChoiceField(
                                        choices=year_choises, 
                                        required = False,
                                        widget=forms.Select())
        self.fields['year_to'] = forms.ChoiceField(
                                        choices=year_choises, 
                                        required = False,
                                        widget=forms.Select())
        
        # scientific_name.
        scientific_name = models.SpeciesObs.objects.values_list(u'scientific_name', flat = True).distinct().order_by(u'scientific_name')
        scientific_name_choises = [('All', 'All')] + [(item, item) for item in scientific_name]
        self.fields['scientific_name'] = forms.ChoiceField(
                                        help_text=u'As reported on various rank.',
                                        choices=scientific_name_choises, 
                                        required = False,
                                        widget=forms.Select())

#         # taxon_kingdom
#         taxon_kingdom = models.SpeciesObs.objects.values_list(u'taxon_kingdom', flat = True).distinct().order_by(u'taxon_kingdom')
#         taxon_kingdom_choises = [('All', 'All')] + [(item, item) for item in taxon_kingdom]
#         self.fields['kingdom'] = forms.ChoiceField(
#                                         choices=taxon_kingdom_choises, 
#                                         required = False,
#                                         widget=forms.Select())
#         # taxon_phylum
#         taxon_phylum = models.SpeciesObs.objects.values_list(u'taxon_phylum', flat = True).distinct().order_by(u'taxon_phylum')
#         taxon_phylum_choises = [('All', 'All')] + [(item, item) for item in taxon_phylum]
#         self.fields['phylum'] = forms.ChoiceField(
#                                         choices=taxon_phylum_choises, 
#                                         required = False,
#                                         widget=forms.Select())
        # taxon_class
        taxon_class = models.SpeciesObs.objects.values_list(u'taxon_class', flat = True).distinct().order_by(u'taxon_class')
        taxon_class_choises = [('All', 'All')] + [(item, item) for item in taxon_class]
        self.fields['class'] = forms.ChoiceField(
                                        help_text=u'Including taxa of lower rank.',
                                        choices=taxon_class_choises, 
                                        required = False,
                                        widget=forms.Select())
        # taxon_order
        taxon_order = models.SpeciesObs.objects.values_list(u'taxon_order', flat = True).distinct().order_by(u'taxon_order')
        taxon_order_choises = [('All', 'All')] + [(item, item) for item in taxon_order]
        self.fields['order'] = forms.ChoiceField(
                                        help_text=u'Including taxa of lower rank.',
                                        choices=taxon_order_choises, 
                                        required = False,
                                        widget=forms.Select())

#         # taxon_genus
#         taxon_genus = models.SpeciesObs.objects.values_list(u'taxon_genus', flat = True).distinct().order_by(u'taxon_genus')
#         taxon_genus_choises = [('All', 'All')] + [(item, item) for item in taxon_genus]
#         self.fields['genus'] = forms.ChoiceField(
#                                         choices=taxon_genus_choises, 
#                                         required = False,
#                                         widget=forms.Select())

        # taxon_species
        taxon_species = models.SpeciesObs.objects.values_list(u'taxon_species', flat = True).distinct().order_by(u'taxon_species')
        taxon_species_choises = [('All', 'All')] + [(item, item) for item in taxon_species]
        self.fields['species'] = forms.ChoiceField(
                                        help_text=u'Including taxa of lower rank.',
                                        choices=taxon_species_choises, 
                                        required = False,
                                        widget=forms.Select())


def parse_filter_params(request_params, db_filter_dict, url_param_list):
    """ """
    #
#     if u'dataset' in request_params:
#         dataset_filter = request_params['dataset']
#         if dataset_filter not in [u'', u'All']:
#             db_filter_dict['{0}__{1}'.format('dataset_name', 'startswith')] = dataset_filter
#             url_param_list.append(u'dataset_name=' + dataset_filter)
    # 'year' can be used for a single year.
    if u'year' in request_params:
        year_from_filter = request_params['year']
        year_to_filter = request_params['year']
        if year_from_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('sampling_year', 'gte')] = year_from_filter
            db_filter_dict['{0}__{1}'.format('sampling_year', 'lte')] = year_to_filter
            url_param_list.append(u'year_from=' + year_from_filter)
            url_param_list.append(u'year_to=' + year_to_filter)
    #
    if u'year_from' in request_params:
        year_from_filter = request_params['year_from']
        if year_from_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('sampling_year', 'gte')] = year_from_filter
            url_param_list.append(u'year_from=' + year_from_filter)
    #
    if u'year_to' in request_params:
        year_to_filter = request_params['year_to']
        if year_to_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('sampling_year', 'lte')] = year_to_filter
            url_param_list.append(u'year_to=' + year_to_filter)
#     # taxon_kingdom
#     if u'kingdom' in request_params:
#         kingdom_filter = request_params['kingdom']
#         if kingdom_filter not in [u'', u'All']:
#             db_filter_dict['{0}__{1}'.format('taxon_kingdom', 'iexact')] = kingdom_filter
#             url_param_list.append(u'kingdom=' + kingdom_filter)
#     # taxon_phylum
#     if u'phylum' in request_params:
#         phylum_filter = request_params['phylum']
#         if phylum_filter not in [u'', u'All']:
#             db_filter_dict['{0}__{1}'.format('taxon_phylum', 'iexact')] = phylum_filter
#             url_param_list.append(u'phylum=' + phylum_filter)
    # taxon_class
    if u'class' in request_params:
        class_filter = request_params['class']
        if class_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('taxon_class', 'iexact')] = class_filter
            url_param_list.append(u'class=' + class_filter)
    # taxon_order
    if u'order' in request_params:
        order_filter = request_params['order']
        if order_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('taxon_order', 'iexact')] = order_filter
            url_param_list.append(u'order=' + order_filter)
#     # taxon_genus
#     if u'genus' in request_params:
#         genus_filter = request_params['genus']
#         if genus_filter not in [u'', u'All']:
#             db_filter_dict['{0}__{1}'.format('taxon_genus', 'iexact')] = genus_filter
#             url_param_list.append(u'genus=' + genus_filter)
    # taxon_species
    if u'species' in request_params:
        genus_filter = request_params['species']
        if genus_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('taxon_species', 'iexact')] = genus_filter
            url_param_list.append(u'species=' + genus_filter)
    #
    if u'scientific_name' in request_params:
        scientific_name_filter = request_params['scientific_name']
        if scientific_name_filter not in [u'', u'All']:
            db_filter_dict['{0}__{1}'.format('scientific_name', 'iexact')] = scientific_name_filter
            url_param_list.append(u'scientific_name=' + scientific_name_filter)
