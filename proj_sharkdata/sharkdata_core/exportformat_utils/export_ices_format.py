#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import traceback
import codecs
import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import sharkdata_core
import app_resources.models as resources_models
import app_exportformats.models as export_models
import app_datasets.models as datasets_models
import app_sharkdataadmin.models as admin_models

@sharkdata_core.singleton
class GenerateIcesXml(object):
    """ Singleton class. """
    
    def __init__(self):
        """ """
        self._ftp_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'datasets')
        self._export_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'exports')
        self._translate_taxa = None
    
    def generateIcesXml(self, logrow_id, 
                        datatype_list, year_from, year_to, status, user):
        """ """
        # Load resource content to translate from DynTaxa to WoRMS.
        self._translate_taxa = TranslateTaxa()
        self._translate_taxa.loadTranslateTaxa('translate_dyntaxa_to_worms')
        
        # Create target directory if not exists.
        if not os.path.exists( self._export_dir_path):
            os.makedirs( self._export_dir_path)
        #
        error_counter = 0
        #
        year_int = int(year_from)
        year_to_int = int(year_to)
        #
        for datatype in datatype_list:
            while year_int <= year_to_int:
                ""
                self.generateOneIcesXml(logrow_id, error_counter, 
                           datatype, unicode(year_int), status, user)
                #
                year_int += 1
        #
        if error_counter > 0:
            admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED (Errors: ' + unicode(error_counter) + ')')
        else:
            admin_models.changeLogRowStatus(logrow_id, status = 'FINISHED')

        if settings.DEBUG: print('DEBUG: ICES-XML generation FINISHED')            
        
    def generateOneIcesXml(self, logrow_id, error_counter, 
                           datatype, year, status, user):
        """ """        
        # Add all rows from all datasets that match datatype and year.
        icesxmlgenerator = IcesXmlGenerator(self._translate_taxa)
        #
        db_datasets = datasets_models.Datasets.objects.all()
        for db_dataset in db_datasets:
            if db_dataset.datatype.upper() != datatype.upper():
                continue
            #
            try:
                zip_file_name = db_dataset.dataset_file_name
                admin_models.addResultLog(logrow_id, result_log = 'Reading archive file: ' + zip_file_name + '...')
                if settings.DEBUG:
                    if settings.DEBUG: print('DEBUG: ICES-ZIP processing: ' + zip_file_name)            
                #
                dataset = sharkdata_core.Dataset()
                dataset.loadDataFromZipFile(zip_file_name,
                                            dataset_dir_path = self._ftp_dir_path,
                                            encoding = 'cp1252')
                #
                dataheader = dataset.data_header
                if settings.DEBUG: print(dataheader)
                #
                datarows = dataset.data_rows
                for datarow in datarows:
                    datarow_dict = dict(zip(dataheader, map(unicode, datarow)))
                    #
                    if datarow_dict.get('visit_year', '') == year:
                        # TODO: Should be codes.
                        national_monitoring_list = ['National marine monitoring',
                                                    'Nationella programmet Bottniska Viken från 2015',
                                                    'Nationella programmet Egentliga Östersjön, Utsjön 2007-']
                        #
                        if datarow_dict.get('sample_project_name_sv', '') in national_monitoring_list:
                        
                            icesxmlgenerator.add_row(datarow_dict)
            #
            except Exception as e:
                error_counter += 1 
                traceback.print_exc()
                admin_models.addResultLog(logrow_id, result_log = 'ERROR: Failed to generate ICES-XML from: ' + zip_file_name + '.')                
        #
        try:
            # Create and save the result.
            out_rows = icesxmlgenerator.create_xml()
            #
            export_name = 'ICES-XML' + '_SMHI_' + datatype + '_' + year
            export_file_name = export_name + '.xml'
            export_file_path = os.path.join(self._export_dir_path, export_file_name)
            error_log_file = export_name + '_log.txt'
            error_log_file_path = os.path.join(self._export_dir_path, error_log_file)
            #
            icesxmlgenerator.save_xml_file(out_rows, export_file_path)
            # Update database.
            # Delete row if exists.
            export_db_rows = export_models.ExportFiles.objects.filter(export_name = export_name)
            for db_row in export_db_rows: 
                db_row.delete()
            #
            approved = False
            if status == 'Checked by DC':
                approved = True # Will not be validated via DATSU.
                
            # Write row.
            dbrow = export_models.ExportFiles(
                            format = 'ICES-XML',
                            datatype = datatype,
                            year = year,
                            approved = approved,
                            status = status,
                            export_name = export_name,
                            export_file_name = export_file_name,
                            export_file_path = export_file_path,
                            error_log_file = error_log_file,
                            error_log_file_path = error_log_file_path,
                            generated_by = user,
                          )
            dbrow.save()
            
            # Log file.
            log_rows = []
            log_rows.append('')
            log_rows.append('')
            log_rows.append('Generate ICES-XML files. ' + unicode(datetime.datetime.now()))
            log_rows.append('')
            log_rows.append('- Format: ' + dbrow.format)
            log_rows.append('- Datatype: ' + unicode(dbrow.datatype))
            log_rows.append('- Year: ' + unicode(dbrow.year))
            log_rows.append('- Status: ' + unicode(dbrow.status))
            log_rows.append('- Approved: ' + unicode(dbrow.approved))
            log_rows.append('- Export name: ' + unicode(dbrow.export_name))
            log_rows.append('- Export file name: ' + unicode(dbrow.export_file_name))
            log_rows.append('')
            #
            icesxmlgenerator.save_log_file(log_rows, error_log_file_path)
        #
        except Exception as e:
            error_counter += 1 
            traceback.print_exc()
            admin_models.addResultLog(logrow_id, result_log = 'ERROR: Failed to generate ICES-XML files. Exception: ' + unicode(e))              

class IcesXmlGenerator(object):
    """ """
    def __init__(self, translate_taxa):
        """ """
        self.datarow_dict = {}
        self._rec20_dict = {}
        self._rec21_dict = {}
        self._translate_taxa = translate_taxa
        # Load resource file containing WoRMS info for taxa.
        self.worms_info_object = sharkdata_core.SpeciesWormsInfo()
        self.worms_info_object.loadSpeciesFromResource()
        #
        self.define_fields_and_keys()

    def add_row(self, datarow_dict):
        """ """
        # Check if parameter should be reported.
        if datarow_dict['parameter'] in self.filter_parameters:
            #
            ices_content = sharkdata_core.ExportIcesContent(datarow_dict, self._translate_taxa)
            ices_content.copy_to_ices_fields()
            ices_content.cleanup_ices_fields()
            ices_content.add_rec20(self._rec20_dict, self.rec20_fields)
            ices_content.add_rec21(self._rec21_dict, self.rec21_fields)
            #
            key38 = self.add_key_strings(datarow_dict)
            if key38 in self.datarow_dict:
                if settings.DEBUG: print('Duplicate found: ' + key38)
            #
            self.datarow_dict[key38] = datarow_dict

    def create_xml(self):
        """ """
        if settings.DEBUG: print('DEBUG: Number of rows: ' + unicode(len(self.datarow_dict.keys())))
        #
        out_rows = []
        # XML header. 
        out_rows.append('<?xml version="1.0" encoding="ISO-8859-1" ?>')
        # XML elements.
        rec00_element = False
        rec90_element = False
        rec91_element = False
#         rec92_element = False
        rec34_element = False
        rec38_element = False
        rec90_lastusedkey = 'first'
        rec91_lastusedkey = 'first'
#         rec92_lastusedkey = 'first'
        rec34_lastusedkey = 'first'
        rec38_lastusedkey = 'first'
        # Iterate over rows. Important note: Sorted by the keys_r38 key.
        for rowdictkey in sorted(self.datarow_dict.keys()):
            rowdict = self.datarow_dict[rowdictkey]
#             if settings.DEBUG: print('DEBUG: Row as dict: ' + unicode(rowdict))
            
            # ===== Rec 00. =====
            if rec00_element == False:
                rec00_element = True
                out_rows.append('<R00.FileInformation>')
                #
                for field in self.rec00_fields:
                    if rowdict.get(field, False):
                        out_rows.append('  <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
            
            # ===== Rec 90. =====
            if rec90_lastusedkey != rowdict.get('rec90_key', ''):
                # Close old.
                if rec38_element == True:
                    out_rows.append('        </R38.BiologicalCommunityAbundance>')
                if rec34_element == True:
                    out_rows.append('      </R34.BiologicalCommunitySample>')
#                 if rec92_element == True:
#                     out_rows.append('      </R92.SiteDescriptionRecord>')
                if rec91_element == True:
                    out_rows.append('    </R91.SamplingEventRecord>')
                if rec90_element == True:
                    out_rows.append('  </R90.SamplingPlatformRecord>')
                rec38_element = False
                rec34_element = False
#                 rec92_element = False
                rec91_element = False
                # Open new.
                rec90_element = True
                rec90_lastusedkey = rowdict.get('rec90_key', '')
                out_rows.append('  <R90.SamplingPlatformRecord>')
                #
                for field in self.rec90_fields:
                    if rowdict.get(field, False):
                        out_rows.append('    <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
            
            # ===== Rec 91. =====
            if rec91_lastusedkey != rowdict.get('rec91_key', ''):
                # Close old.
                if rec38_element == True:
                    out_rows.append('        </R38.BiologicalCommunityAbundance>')
                if rec34_element == True:
                    out_rows.append('      </R34.BiologicalCommunitySample>')
#                 if rec92_element == True:
#                     out_rows.append('      </R92.SiteDescriptionRecord>')
                if rec91_element == True:
                    out_rows.append('    </R91.SamplingEventRecord>')
                rec38_element = False
                rec34_element = False
#                 rec92_element = False
                # Open new.
                rec91_element = True
                rec91_lastusedkey = rowdict.get('rec91_key', '')
                out_rows.append('    <R91.SamplingEventRecord>')
                #
                for field in self.rec91_fields:
                    if rowdict.get(field, False):
                        out_rows.append('      <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
            
#             # ===== Rec 92. =====
#             if rec92_lastusedkey != rowdict.get('rec92_key', ''):
#                 # Close old.
#                 if rec38_element == True:
#                     out_rows.append('        </R38.BiologicalCommunityAbundance>')
#                 if rec34_element == True:
#                     out_rows.append('      </R34.BiologicalCommunitySample>')
#                 if rec92_element == True:
#                     out_rows.append('      </R92.SiteDescriptionRecord>')
# #                 if rec91_element == True:
# #                     out_rows.append('    </R91.SamplingEventRecord>')
#                 rec38_element = False
#                 rec34_element = False
# #                 rec91_element = False
#                 # Open new.
#                 rec92_element = True
#                 rec92_lastusedkey = rowdict.get('rec92_key', '')
#                 out_rows.append('      <R92.SiteDescriptionRecord')
#                 #
#                 for field in self.rec92_fields:
#                     if rowdict.get(field, False):
#                         out_rows.append('        <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
            
            # ===== Rec 34. =====
            if rec34_lastusedkey != rowdict.get('rec34_key', ''):
                # Close old.
                if rec38_element == True:
                    out_rows.append('        </R38.BiologicalCommunityAbundance>')
                if rec34_element == True:
                    out_rows.append('      </R34.BiologicalCommunitySample>')
#                 if rec92_element == True:
#                     out_rows.append('      </R92.SiteDescriptionRecord>')
#                     out_rows.append('      </R92.SiteDescriptionRecord>')
                rec38_element = False
                rec34_element = False
#                 rec92_element = False
                # Open new.
                rec34_element = True
                rec34_lastusedkey = rowdict.get('rec34_key', '')
                out_rows.append('      <R34.BiologicalCommunitySample>')
                #
                for field in self.rec34_fields:
                    if rowdict.get(field, False):
                        out_rows.append('        <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
            
            # ===== Rec 38. =====
            if rec38_lastusedkey != rowdict.get('rec38_key', ''):
                # Close old.
                if rec38_element == True:
                    out_rows.append('        </R38.BiologicalCommunityAbundance>')
                # Open new.
                rec38_element = True
                rec38_lastusedkey = rowdict.get('rec38_key', '')
                out_rows.append('        <R38.BiologicalCommunityAbundance>')
                #
                for field in self.rec38_fields:
                    if rowdict.get(field, False):
                        out_rows.append('          <' + field + '>' + rowdict.get(field, '') + '</' + field + '>')
        #
        if rec38_element:
            out_rows.append('        </R38.BiologicalCommunityAbundance>')
        if rec34_element:
            out_rows.append('      </R34.BiologicalCommunitySample>')
#         if rec92_element == True:
#             out_rows.append('      </R92.SiteDescriptionRecord>')
        if rec91_element:
            out_rows.append('    </R91.SamplingEventRecord>')
        if rec90_element:
            out_rows.append('  </R90.SamplingPlatformRecord>')
        #    
        if len(self._rec20_dict) > 0:
            for key in self._rec20_dict.keys():
                out_rows.append('  <R20.SamplingMethod>')
                r20_dict = self._rec20_dict[key]
                r20_dict['SMLNK'] = r20_dict['sequence_number']
                for field in self.rec20_fields:
                    if r20_dict.get(field, False):
                        out_rows.append('    <' + field + '>' + r20_dict.get(field, '') + '</' + field + '>')
                out_rows.append('  </R20.SamplingMethod>')
        #    
        if len(self._rec21_dict) > 0:
            for key in self._rec21_dict.keys():
                out_rows.append('  <R21.AnalyticalMethod>')
                r21_dict = self._rec21_dict[key]
                r21_dict['AMLNK'] = r21_dict['sequence_number']
                for field in self.rec21_fields:
                    if r21_dict.get(field, False):
                        out_rows.append('    <' + field + '>' + r21_dict.get(field, '') + '</' + field + '>')
                out_rows.append('  </R21.AnalyticalMethod>')
        #    
        if rec00_element:
            out_rows.append('</R00.FileInformation>')
        # 
        return out_rows

    def save_xml_file(self, out_rows, file_path_name, 
                      encoding = 'cp1252', row_separator = '\r\n'):
        """ """
        outfile = None
        try:
            outfile = codecs.open(file_path_name, mode = 'w', encoding = encoding)
            for row in out_rows:
                outfile.write(row + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write XML file: " + file_path_name)
        finally:
            if outfile: outfile.close()

    def save_log_file(self, out_rows, file_path_name, 
                      encoding = 'cp1252', row_separator = '\r\n'):
        """ """
        outfile = None
        try:
            outfile = codecs.open(file_path_name, mode = 'w', encoding = encoding)
            for row in out_rows:
                outfile.write(row + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write log file: " + file_path_name)
        finally:
            if outfile: outfile.close()

    def add_key_strings(self, row_dict):
        """ Adds all needed keys to the dictionary. Returns key for the row. """
        # Create key values.
        rec00_key = self.create_key_string(row_dict, self.rec00_keys)
        rec90_key = self.create_key_string(row_dict, self.rec90_keys)
        rec91_key = self.create_key_string(row_dict, self.rec91_keys)
#         rec92_key = self.create_key_string(row_dict, self.rec92_keys)
        rec34_key = self.create_key_string(row_dict, self.rec34_keys)
        rec38_key = self.create_key_string(row_dict, self.rec38_keys)
        rec20_key = self.create_key_string(row_dict, self.rec20_keys)
        rec21_key = self.create_key_string(row_dict, self.rec21_keys)
        rec94_key = self.create_key_string(row_dict, self.rec94_keys)
        # Add keys to dict.
        row_dict['rec00_key'] = rec00_key
        row_dict['rec90_key'] = rec90_key
        row_dict['rec91_key'] = rec91_key
#         row_dict['rec92_key'] = rec92_key
        row_dict['rec34_key'] = rec34_key
        row_dict['rec38_key'] = rec38_key
        row_dict['rec20_key'] = rec20_key
        row_dict['rec21_key'] = rec21_key
        row_dict['rec94_key'] = rec94_key
        #
        return rec38_key

    def define_fields_and_keys(self):
        """ """
        # Parameters for export.
        self.filter_parameters = ['# counted', 'Wet weight']
        # ICES fields definitions.
        self.rec00_fields = ['RLABO', 'CNTRY', 'MYEAR', 'RFVER']
        self.rec90_fields = ['SHIPC', 'CRUIS', 'Owner', 'PRDAT']
        self.rec91_fields = ['STNNO', 'LATIT', 'LONGI', 'POSYS', 'SDATE', 'STIME', 'ETIME', 'WADEP', 'STATN', 'MPROG', 'WLTYP', 'MSTAT', 'PURPM', 'EDATE']
        self.rec92_fields = ['MATRX', 'PARAM', 'MUNIT', 'VALUE']
        self.rec34_fields = ['DTYPE', 'SMPNO', 'SMLNK', 'ATIME', 'NOAGG', 'FNFLA', 'FINFL', 'SMVOL', 'SUBST', 'DEPOS', 'PCNAP', 'PRSUB', 'TRSCS', 'TRSCE', 'TRCSD', 'TRCED']
        self.rec38_fields = ['MNDEP', 'MXDEP', 'SPECI', 'RLIST', 'SFLAG', 'STAGE', 'SEXCO', 'PARAM', 'MUNIT', 'VFLAG', 'QFLAG', 'VALUE', 'AMLNK']
        self.rec20_fields = ['SLABO', 'SMLNK', 'SMTYP', 'MESHS', 'SAREA', 'LNSMB']
        self.rec21_fields = ['AMLNK', 'ALABO', 'METDC', 'REFSK', 'METST', 'METFP', 'METPT', 'METOA', 'FORML', 'ACCRD']
        self.rec94_fields = ['ICLNK', 'ICCOD', 'ICLAB']
        # Key definitions.
        self.rec00_keys = []
        self.rec90_keys = ['CRUIS']
        self.rec91_keys = ['CRUIS', 'STNNO']
        self.rec92_keys = ['CRUIS', 'STNNO']
        self.rec34_keys = ['CRUIS', 'STNNO', 'TRANS', 'SMPNO']
        self.rec38_keys = ['CRUIS', 'STNNO', 'TRANS', 'SMPNO', 'MNDEP', 'MXDEP', 'SPECI', 'SIZCL', 'STAGE', 'SEXCO', 'PARAM', 'MUNIT']
        self.rec20_keys = ['SMLNK']
        self.rec21_keys = ['AMLNK']
        self.rec94_keys = ['AMLNK', 'ICLNK']

    def create_key_string(self, row_dict, key_columns):
        """ Util: Generates the key for one row. """
        key_string = ''
        try:
            key_list = [unicode(row_dict.get(item, '')) for item in key_columns]
            key_string = '+'.join(key_list)
        except:
            key_string = 'ERROR: Failed to generate key-string'
        # Replace swedish characters.
        key_string = key_string.replace('Å', 'A')
        key_string = key_string.replace('Ä', 'A')
        key_string = key_string.replace('Ö', 'O')
        key_string = key_string.replace('å', 'a')
        key_string = key_string.replace('ä', 'a')
        key_string = key_string.replace('ö', 'o')
        key_string = key_string.replace('µ', 'u')
        #
        return key_string

class TranslateTaxa():
    """ """
    def __init__(self):
        """ """
        self.translate_taxa_dict = {}
         
    def getTranslatedTaxaAndRlist(self, scientific_name):
        """ """
        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        else:
            print('DEBUG: TranslateTaxa, not found: ' + scientific_name)
            return ('', '')
         
    def loadTranslateTaxa(self, resource_name):
        """ """
        self.translate_taxa_dict = {}
        #
        resource = None
        try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
        except ObjectDoesNotExist: resource = None
        #
        if resource:
            data_as_text = resource.file_content # .encode('cp1252')
            header = []
            for index, row in enumerate(data_as_text.split('\n')):
                row = [item.strip() for item in row.split('\t')]
                if index == 0:
                    # Supposed to be at least 'dyntaxa_scientific_name', 'worms_aphia_id', 'ices_rlist'.
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        self.translate_taxa_dict[row_dict.get('dyntaxa_scientific_name', '')] = \
                            (row_dict.get('worms_aphia_id', ''), row_dict.get('ices_rlist', ''))

