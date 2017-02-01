#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

import os
import os.path
import threading
from lxml import etree
from django.conf import settings
import app_datasets.models as models
import sharkdata_core


@sharkdata_core.singleton
class MetadataUtils(object):
    """ Singleton class. """
    def __init__(self):
        """ """
        self._xslt_dir_path = os.path.join(settings.APP_DATASETS_FTP_PATH, 'xslt')

    def metadataToIso19139(self, metadata_as_text):
        """ Metadata to XML. """
        xslfile = os.path.join(self._xslt_dir_path, 'shark_metadata_iso_19139.xslt')
         
        metadata_as_xml = self._metadataTextToXml(metadata_as_text, "SharkMetadata")
        print('\n\n' + 'Metadata as XML: ' + etree.tostring(metadata_as_xml))
         
        # Transform.
        xsl_file = os.path.abspath(xslfile).replace('\\','/')
        xsl = etree.parse(xsl_file)
        xslt = etree.XSLT(xsl)
        metadata_as_iso19139 =  xslt(metadata_as_xml)
        #
        print('\n\n' + str(metadata_as_iso19139))
        return metadata_as_iso19139
     
    def _metadataTextToXml(self, metadata_as_text, rootname):
        """ Transform a metadata record to a flat XML string. """
     
        metadata_dict = {}
        for row in metadata_as_text.split('\r\n'):
            if ':' in row:
                
                #row = unicode(row.decode('cp1252'))
                
                parts = row.split(':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_dict[key] = value
            
        root = etree.Element(rootname)
     
        for key in metadata_dict.keys():
            
            col=key.replace(' ', '_')
            dat=''
            try:
                dat=str(metadata_dict[key]) # may need to be careful of unicode encoding issues when reading data from Excel
            except:
                ####dat=str(metadata_dict[key.decode('cp1252', 'replace')])
                dat=str('ERROR when decoding.')
                
            # TODO: Split on '#' to create lists. Used for lists of Parameters/units.
        
            if '#' not in key:

                child=etree.SubElement(root, unicode(col))
                child.text=unicode(dat)

        return root

# EXAMPLE CODE:
# 
# <root atr="100">
#   text1
#   <child atr="atr">
#     <superchild atr="">sctext1</superchild>
#     tail1
#     tail2
#   </child>
#   tail
#   <child atr="">text</child>
# </root>
# 
# root = Element('root', atr=str(100))
# root.text = 'text1'
# child = SubElement(root, 'child', atr="atr")
# superchild = SubElement(root, 'superchild', atr="" if value is None else value)
# superchild.text = 'sctext1'
# superchild.tail = 'tail1'
# superchild.tail += 'tail2'
# child.tail = 'tail'
# child = SubElement(root, 'child', atr="")
# child.text = 'text'


