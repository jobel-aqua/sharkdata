#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import datetime

class ExportIcesContent(object):
    """ """
    def __init__(self, datarow_dict, translate_taxa):
        """ """
        self._dict = datarow_dict
        self._translate_taxa = translate_taxa
    
    def copy_to_ices_fields(self):
        """ """
#         for key in self._dict.keys():
#             print('DEBUG ' + key + ': ' + self._dict[key])
        # R00.FileInformation
        self._dict['RLABO'] = 'SMHI'
        self._dict['CNTRY'] = '77'
        self._dict['MYEAR'] = self._dict.get('visit_year', ''). replace('-', '') # Format YYYYMMDD.
        self._dict['RFVER'] = '3.2.5'
    
        # R90.SamplingPlatformRecord
        self._dict['SHIPC'] = self._dict.get('platform_code', '')
        self._dict['CRUIS'] = self._dict.get('', '')  # Will be generated in ices_expedition_key().
        self._dict['Owner'] = 'SWAM'
        self._dict['PRDAT'] = unicode(datetime.date.today()). replace('-', '') # Format YYYYMMDD.
    
        # R91.SamplingEventRecord
        self._dict['STNNO'] = self._dict.get('station_name', '') + '-' + self._dict.get('visit_date', '') # TODO: Check this.
#         self._dict['LATIT'] = self._dict.get('sample_latitude_dm', '')
#         self._dict['LONGI'] = self._dict.get('sample_longitude_dm', '')
        self._dict['LATIT'] = self._dict.get('sample_latitude_dd', '')
        self._dict['LONGI'] = self._dict.get('sample_longitude_dd', '')
        self._dict['POSYS'] = self._dict.get('positioning_system_code', '')
        
        self._dict['SDATE'] = self._dict.get('sample_date', '')
    
        self._dict['STIME'] = '' # Not used.
        self._dict['ETIME'] = '' # Not used.
        self._dict['WADEP'] = self._dict.get('water_depth_m', '')
        self._dict['STATN'] = self._dict.get('station_name', '')
        self._dict['MPROG'] = self._dict.get('monitoring_program_code', '')
        self._dict['WLTYP'] = '' # Not used.
        self._dict['MSTAT'] = self._dict.get('station_type_code', '')
        self._dict['PURPM'] = self._dict.get('purpose_code', '')
        self._dict['EDATE'] = '' # Not used.
    
        # R92.SiteDescriptionRecord
        self._dict['MATRX'] = '' # Not used.
#         self._dict['PARAM'] = '' # Not use.
#         self._dict['MUNIT'] = '' # Not used.
#         self._dict['VALUE'] = '' # Not used.
    
        # R34.BiologicalCommunitySample
        self._dict['DTYPE'] = self._dict.get('delivery_datatype', '')
        self._dict['SMPNO'] = self._dict.get('sample_id', '')
#         self._dict['SMLNK'] = self._dict.get('', '') # Will be generated in add_rec20().
        self._dict['ATIME'] = self._dict.get('sample_time', '')
        self._dict['NOAGG'] = self._dict.get('aggregated_subsamples', '')
        self._dict['FNFLA'] = self._dict.get('fauna_flora_found', '')
        self._dict['FINFL'] = self._dict.get('factors_influencing_code', '')
        self._dict['SMVOL'] = self._dict.get('sampled_volume_l', '') # TODO: m3 if ZP, else L. 
        self._dict['SUBST'] = '' # Not used.
        self._dict['DEPOS'] = self._dict.get('sediment_deposition_code', '')
        self._dict['PCNAP'] = '' # Not used.
        self._dict['PRSUB'] = '' # Not used.
        self._dict['TRSCS'] = self._dict.get('section_distance_start', '')
        self._dict['TRSCE'] = self._dict.get('section_distance_end', '')
        self._dict['TRCSD'] = self._dict.get('section_start_depth_m', '')
        self._dict['TRCED'] = self._dict.get('section_end_depth_m', '')
    
        # R38.BiologicalCommunityAbundance
        self._dict['MNDEP'] = self._dict.get('sample_min_depth_m', '')
        self._dict['MXDEP'] = self._dict.get('sample_max_depth_m', '')
        self._dict['SPECI'] = self._dict.get('scientific_name', '')
        self._dict['RLIST'] = self._dict.get('', '') # Will be generated later.
        self._dict['SFLAG'] = self._dict.get('species_flag_code', '')
        self._dict['STAGE'] = self._dict.get('dev_stage_code', '')
        self._dict['SEXCO'] = self._dict.get('sex_code', '')
        self._dict['PARAM'] = self._dict.get('parameter', '')
        self._dict['MUNIT'] = self._dict.get('unit', '')
        self._dict['VFLAG'] = '' # Not used.
        self._dict['QFLAG'] = self._dict.get('quality_flag', '')
        self._dict['VALUE'] = self._dict.get('value', '')
#         self._dict['AMLNK'] = self._dict.get('', '') # Will be generated in add_rec21().
      
        # R20.SamplingMethod
        self._dict['SLABO'] = self._dict.get('sampling_laboratory_code', '')
#         self._dict['SMLNK'] = self._dict.get('', '') # Will be generated in add_rec20().
        self._dict['SMTYP'] = self._dict.get('sampler_type_code', '')
        self._dict['MESHS'] = self._dict.get('mesh_size_um', '')
        self._dict['SAREA'] = self._dict.get('sampler_area_cm2', '')
        self._dict['LNSMB'] = '' # Not used.
    
        # R21.AnalyticalMethod
#         self._dict['AMLNK'] = self._dict.get('', '') # Will be generated in add_rec21().
        self._dict['ALABO'] = self._dict.get('analytical_laboratory_code', '')
        self._dict['METDC'] = self._dict.get('method_documentation', '')
        self._dict['REFSK'] = self._dict.get('reference_source_code', '')
        self._dict['METST'] = self._dict.get('storage_method_code', '')
        self._dict['METFP'] = self._dict.get('preservation_method_code', '')
        self._dict['METPT'] = '' # Not used.
        self._dict['METOA'] = self._dict.get('analysis_method_code', '')
        self._dict['FORML'] = '' # Not used.
        self._dict['ACCRD'] = '' # Not used.
        self._dict['ACORG'] = '' # Not used.
    
        # R94.Intercomparison
        self._dict['ICLNK'] = '' # Not used.
        self._dict['ICCOD'] = '' # Not used.
        self._dict['ICLAB'] = '' # Not used.

    def cleanup_ices_fields(self):
        """ """
        if not self._dict['MPROG']:  self._dict['MPROG'] = 'NATL'
        if not self._dict['SMPNO']:  self._dict['SMPNO'] = '9999'
        #
        self._dict['METDC'] = ''
        self._dict['REFSK'] = 'HC-C-C8'
        #
        if not self._dict['ALABO']:  self._dict['ALABO'] = self._dict.get('analytical_laboratory_name_sv', '')
        if not self._dict['SLABO']:  self._dict['SLABO'] = self._dict.get('sampling_laboratory_name_sv', '')
        #
        alabo = self._dict['ALABO']
        if alabo == 'Umeå University':
            self._dict['ALABO'] = 'UMSC'
        if alabo == 'The Sven Lovén Centre for Marine Sciences-Kristineberg':
            self._dict['ALABO'] = 'KMFS'
        if alabo == 'Stockholm University Department of Ecology Environment and Plant Sciences':
            self._dict['ALABO'] = 'SUSE'
#         else:
#             self._dict['ALABO'] = 'SMHI'
        #
        slabo = self._dict['SLABO']
        if slabo == 'Umeå University':
            self._dict['SLABO'] = 'UMSC'
        if slabo == 'The Sven Lovén Centre for Marine Sciences-Kristineberg':
            self._dict['SLABO'] = 'KMFS'
        if slabo == 'Stockholm University Department of Ecology Environment and Plant Sciences':
            self._dict['SLABO'] = 'SUSE'        
        #
        if not self._dict['SHIPC']:
            self._dict['SHIPC'] = 'AA30' # Unspecified ship.
        #
        self._dict['SDATE'] = self.ices_date(self._dict['SDATE'])
        #
        self._dict['STIME'] = self.ices_time(self._dict['STIME'])
#         #
#         self._dict['LATIT'] = self.ices_lat_long(self._dict['LATIT'])
#         #
#         self._dict['LONGI'] = self.ices_lat_long(self._dict['LONGI'])
        #
        self._dict['DTYPE'] = self.ices_datatype(self._dict['DTYPE'])
        #
        self._dict['PARAM'] = self.ices_parameter_name(self._dict['PARAM'])
        #
        self._dict['MUNIT'] = self.ices_unit_name(self._dict['MUNIT'])
        #
        self._dict['FNFLA'] = self.ices_fauna_flora_found(self._dict['FNFLA'])
        #
        (aphiaid, rlist) = self.translate_scientific_name_to_aphia_id(self._dict['SPECI'])
        self._dict['SPECI'] = aphiaid
        self._dict['RLIST'] = rlist
        #
        # Add depth if missing.
        if self._dict['DTYPE'] == 'ZB':
            if len(self._dict['WADEP']) == 0:
                self._dict['WADEP'] = self._dict['MNDEP']
            # In Zoobenthos: MNDEP = Upper depth of sediment sample.
            self._dict['MNDEP'] = ''
            # In Zoobenthos: MXDEP = Lower depth of sediment sample.
            self._dict['MXDEP'] = ''
        # Generate expedition key.
        self._dict['CRUIS'] = self.ices_expedition_key()
        
    def add_rec20(self, rec20_dict, rec20_fields):
        """ """
#         self.rec20_fields = ['SLABO', 'SMLNK', 'SMTYP', 'MESHS', 'SAREA', 'LNSMB']
        #
        r20_key_list = []
        r20_dict = {}
        for key in rec20_fields:
            r20_key_list.append(unicode(self._dict.get(key, '')))
            r20_dict[key] = self._dict.get(key, '')
        #
        r20_key = '-'.join(r20_key_list)
        if r20_key not in rec20_dict:
            rec20_dict[r20_key] = r20_dict
            sequence_number = unicode(len(rec20_dict))
            rec20_dict[r20_key]['sequence_number'] = sequence_number
        #
        self._dict['SMLNK'] = rec20_dict[r20_key]['sequence_number']
        
    def add_rec21(self, rec21_dict, rec21_fields):
        """ """
#         self.rec21_fields = ['AMLNK', 'ALABO', 'METDC', 'REFSK', 'METST', 'METFP', 'METPT', 'METOA', 'FORML', 'ACCRD']
        #
        r21_key_list = []
        r21_dict = {}
        for key in rec21_fields:
            r21_key_list.append(unicode(self._dict.get(key, '')))
            r21_dict[key] = self._dict.get(key, '')
        #
        r21_key = '-'.join(r21_key_list)
        if r21_key not in rec21_dict:
            rec21_dict[r21_key] = r21_dict
            sequence_number = unicode(len(rec21_dict))
            rec21_dict[r21_key]['sequence_number'] = sequence_number
        #
        self._dict['AMLNK'] = rec21_dict[r21_key]['sequence_number']
        
    # ===== Utils =====
    
    def translate_scientific_name_to_aphia_id(self, scientific_name):
        """ """
        (aphiaid, rlist) = self._translate_taxa.getTranslatedTaxaAndRlist(scientific_name)
        
        if aphiaid == '':
            return (scientific_name, 'ER')
        #
        return (aphiaid, rlist)

    def ices_expedition_key(self):
        """ """
        key_list = []
        # Part 1.
        key_list.append(self._dict.get('MYEAR', '')) # 
        key_list.append(self._dict.get('RLABO', '')) # visit.getParent().getReporting_institute_code()
        key_list.append(self._dict.get('DTYPE', '')) # IcesUtil.convertToIcesDatatype(visit
        # Part 2.
        key_list.append(self._dict.get('SHIPC', ''))
        # Part 3.
        month = self._dict.get('SDATE', 'YYYYMMDD')[4:6]
        key_list.append(month)
        #
        key = '-'.join(key_list)
        return key

    
    def ices_tilde(self, value):
        """ """
        # ICES use ~ as delimiter if multiple flags are used.
        tmp_string = value.strip()
        if ',' in tmp_string:
            return tmp_string.replace(',', '~').replace(' ', '')
        if ' ' in tmp_string:
            return tmp_string.replace(' ', '~')
        #
        return tmp_string
    
    def ices_date(self, date):
        """ """
        ices_date = date.replace('-', '')
        return ices_date
    
    def ices_time(self, time):
        """ """
        ices_time = time.replace(':', '')
        return ices_time
    
#     def ices_lat_long(self, lat_long):
#         """ """
#         latlong = lat_long.replace(' ', '')
#         return latlong
    
    def ices_datatype(self, long_name):
        """ """
        datatype = '<<NO DATATYPE FOUND>>'
        if long_name == 'Phytobenthos': datatype = 'PB'
        elif long_name == 'Epibenthos': datatype = 'PB'
        elif long_name == 'Phytoplankton': datatype = 'PP'
        elif long_name == 'Zoobenthos': datatype = 'ZB'
        elif long_name == 'Zooplankton': datatype = 'ZP'
        #
        return datatype
    
    def ices_parameter_name(self, value):
        """ """
        if value == '# counted': return 'ABUNDNR'
        elif value == 'Wet weight': return 'BMWETWT'
        elif value == 'Biovolume concentration': return 'BMCVOL' # PP: Biovolume concentration, mm3/l, BMCVOL.
        elif value == 'Carbon concentration': return 'BMCCONT' # PP: Carbon concentration, ugC/l, BMCCONT.
        elif value == 'Cover (%)': return 'ABUND%C' # Epibenthos.
        #
        return value
    
    def ices_unit_name(self, unit_name):
        """ """
        if unit_name == 'nr/l': return 'nr/dm3'
        elif unit_name == 'ind': return 'nr'
        elif unit_name == 'ind/analysed sample fraction': return 'nr'
        elif unit_name == 'g/analysed sample fraction': return 'g'
          
        elif unit_name == 'mg/analysed sample fraction': 
            if self._dict['parameter'] == 'Wet weight':
                return 'g'
        #  
        return unit_name
    
    def convert_litre_to_m3(self, number):
        """ """
        try:
            m3 = float(number) / 1000
            return unicode(m3)            
        except:
            return ''
     
    # //def separate_purpose_code(purpose):
    # //        // Note: Purpose is a single character code. If more than one ICES want them to be
    # //        // separated by ~.
    # //        String separated = purpose.trim();
    # //        if (!purpose.equals("")) {
    # //            // If space or comma is used.
    # //            separated = separated.replace(",", "~");
    # //            separated = separated.replace(" ", "~");
    # //            
    # //            // If no separation between codes.
    # //            if (!separated.contains("~")) {
    # //                separated = purpose.substring(0, 1);
    # //                for (int i = 1; i < purpose.length(); i++ ) {
    # //                    separated = separated + "~" + purpose.substring(i, i+1);
    # //                }
    # //            }        
    # //        }
    # //        return separated;
    # //    }
    # //    
    
    def fix_sample_number(self, value):
        """ """
        if not value:
            return '0' # ICES needs a value. 
        elif len(value) > 12:
            # SMHI PP contains longer id:s than accepted by ICES. Remove middle part.
            first_and_last_part = value[0, 5] + '--' + value[-5:]
            return first_and_last_part  
        #
        return value.replace(',', '.')
    
    def transform_value(self, variable):
        """ """
    #         if (variable.getParameter().equals("Wet weight") &&
    #              variable.getUnit().equals("mg/analysed sample fraction")) {
    #                 Double value = variable.getValueAsDouble() / 1000.0
    #                 return ConvUtils.convDoubleToString(value)
    #             }
    #         return variable.getValue()
    #     }
    
    def ices_fauna_flora_found(self, value):
        """ """
        if value == '0': return 'Y'
        if value == '1': return 'N'
        return value
    
    def ices__sediment_deposit(self, value):
        """ """
        # DEPOS, Sediment deposit.
        if value == '1': return 'N'
        if value == '2': return 'L'
        if value == '3': return 'M'
        if value == '4': return 'H'
        return value
        
    def ices__quality_flag(self, value):
        """ """
        delimiter = ' '
        if ',' in value: delimiter = ','
        parts = value.trim().split(delimiter)
        
        string_list = []
        for part in parts:
            part = parts.trim()
            if not part:
                pass
            elif part =='A':
                pass # 'A' should not be reported to ICES.
            elif part == 'S':
                string_list.append("<<S:suspect value>>") # Indicator for manual removal of QFLAG or rec38-row.
            else:
                string_list.append(part) # Indicator for manual removal of QFLAG or rec38-row.
        #
        return '~'.join(string_list)
    
    def is_kindom_animalia(self):
        """ """
        if 'Animalia' in self._dict.get('taxon_hierarchy', ''):
            return True
        #
        return False

    def get_transect_length_by_checking_sections(self, sample):
        """ """
    # TODO: Convert from Java:
    #         String transectId = sample.getField("sample.transect_id");
    #         Double maxDistance = sample.getFieldAsDouble("sample.section_distance_end_m");
    #         for (Sample sampleItem : sample.getParent().getSamples()) {
    #             String tmpTransectId = sampleItem.getField("sample.transect_id");
    #             Double tmpMaxDistance = sampleItem.getFieldAsDouble("sample.section_distance_end_m");
    #             if ((maxDistance != null) && (tmpMaxDistance != null)) {
    #                 if (transectId.equals(tmpTransectId)) {                
    #                     if (maxDistance < tmpMaxDistance) {
    #                         maxDistance = tmpMaxDistance;
    #                     }
    #                 }
    #             }
    #         }
    #         if (maxDistance == null) {
    #             return "";
    #         } else {
    #             return maxDistance.toString();
    #         }
    #     }
    
    def get_transect_length_by_sample_max_depths(self, sample):
        """ """
    # TODO: Convert from Java:
    #         String transectId = sample.getField("sample.transect_id");
    #         Double maxDepth = sample.getFieldAsDouble("sample.sample_max_depth_m");
    #         for (Sample sampleItem : sample.getParent().getSamples()) {
    #             String tmpTransectId = sampleItem.getField("sample.transect_id");
    #             Double tmpMaxDepth = sampleItem.getFieldAsDouble("sample.sample_max_depth_m");
    #             if ((maxDepth != null) && (tmpMaxDepth != null)) {
    #                 if (transectId.equals(tmpTransectId)) {                
    #                     if (maxDepth < tmpMaxDepth) {
    #                         maxDepth = tmpMaxDepth;
    #                     }
    #                 }
    #             }
    #         }
    #         if (maxDepth == null) {
    #             return "";
    #         } else {
    #             return maxDepth.toString();
    #         }
    #     }
