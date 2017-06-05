# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import os
import json
from zipfile import ZipFile

import mimetypes
mimetypes.init()

from lxml import etree as ET
import logging
logger = logging.getLogger(__name__)

from django.utils.text import get_valid_filename

from publish_utils import PublisherMixin, PublisherExtensions, ReleasePublisherExtensions
from common import kolektiTests, XSLExtensions, LOCAL_ENCODING, KolektiValidationError
from kolekti import plugins

logger = logging.getLogger(__name__)

class TranslationImporter(kolektiTests):

    html = "{http://www.w3.org/1999/xhtml}"
    
    def __get_path(self, path, release, lang):
        pathparts = path.split('/')
        try:
            return path.split('sources/%s/'%lang)[1]
        except IndexError:
            raise KolektiValidationError('wrong path in zip file')
        
    def __checkfile(self, filepath, filec, importfiletype, release, lang):
        logger.debug('checkfile %s %s',filepath, importfiletype)
        projectfile = filepath
        if '/' in filepath:
            projectfile = self.__get_path(filepath, release, lang)
        if importfiletype in ("text/html", "text/xml", "application/xml"):
            try:
                xml = ET.fromstring(filec)
            except:
                raise KolektiValidationError('xml parse error')
            logger.debug(xml.tag)
            # test if assembly
            if xml.tag == self.html + 'html':
                self.test_xml(xml,"assembly")
                
                projectfile = "/releases/" + release + '/sources/' + lang +'/assembly/' + release +'_asm.html'
                xhead = xml.xpath('/h:html/h:head', namespaces = self.namespaces)[0]
                xbody = xml.xpath('/h:html/h:body', namespaces = self.namespaces)[0]
                xbody.set('lang', lang)
                xbody.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                try:
                    xmetalang = xml.xpath('/h:html/h:html/h:meta[@name="LANG"][@scheme="condition"]',
                                              namespaces = self.namespaces)[0]
                    xmetalang.set('content',lang)
                except IndexError:
                    ET.SubElement(xhead, '{http://www.w3.org/1999/xhtml}meta', {"scheme":"condition","name":"LANG","content":lang})
                self.makedirs(self.dirname(projectfile))
                self.xwrite(xml, projectfile, pretty_print=False, sync = False)
                
            if xml.tag == 'variables':
                self.test_xml(xml,'variables')
                projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
                self.makedirs(self.dirname(projectfile))
                logger.debug(projectfile)
                self.write(filec, projectfile, sync = False)
                
        if importfiletype[:6] == "image":
            projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
            self.makedirs(self.dirname(projectfile))
            self.write(filec, projectfile, sync = False)
        logger.debug(projectfile)
        return projectfile

    
    def import_files(self, path, importfile, importfiletype, release, lang):
        logger.debug("%s/%s %s", path, importfile, importfiletype)
        files = []
        
        if importfiletype == "application/zip":
            z = ZipFile(os.path.join(path, importfile))
            for ifilename in z.namelist():
                logger.debug(ifilename)
                ifilec = z.read(ifilename)
                filetype = mimetypes.guess_type(ifilename)[0]
                projectfile = self.__checkfile(ifilename, ifilec, filetype, release, lang)
                files.append(projectfile)
                #self.write(ifilec, projectfile, "wb", sync = False)
        else:
            with open(os.path.join(path, importfile)) as f:
                ifilec = f.read() 
            projectfile = self.__checkfile(importfile, ifilec, importfiletype, release, lang)
            files.append(projectfile)
            #self.write(ifilec, projectfile, "wb", sync = False)
        return files
    
    def commit(self, files):
        pass

    def rollback(self, files):
        pass
