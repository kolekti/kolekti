# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

from datetime import datetime
import time
import urllib
import re
import os
import copy
import logging
logger = logging.getLogger(__name__)

import json
import unidecode
from lxml import etree as ET

from common import kolektiBase, XSLExtensions, LOCAL_ENCODING
from adapters.mediawiki import AdapterMediawiki


class PublishException(Exception):
    pass

class PublisherMixin(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}
    def __init__(self, *args, **kwargs):
        # intercept lang & draft parameters

        self._publang = None
#        print "mixin",kwargs
        if kwargs.has_key('lang'):
            self._publang = kwargs.get('lang')
            kwargs.pop('lang')

        self._author = "Unknown"
        if kwargs.has_key('author'):
            self._publang = kwargs.get('author')
            kwargs.pop('author')

        self._draft = False
    
        super(PublisherMixin, self).__init__(*args, **kwargs)

        if self._publang is None:
            self._publang = self.config.get("sourcelang","en")

        self.scriptdefs = ET.parse(os.path.join(self._appdir,'pubscripts.xml')).getroot()

                        
    def process_path(self, path):
        return self.substitute_criteria(path, ET.XML('<criteria/>'))

    def substitute_criteria(self, string, profile, extra={}, from_root=True, from_profile=True):
        extra.update({"LANG":self._publang})
        return super(PublisherMixin, self).substitute_criteria(
            string, profile,
            extra=extra,
            from_root=from_root,
            from_profile=from_profile)

    def _substscript(self, s, subst, profile):
        """substitues all _NAME_ by its profile value in string s""" 
        for k,v in subst.iteritems():
            s = s.replace('_%s_'%k,v)
        return self.substitute_variables(self.substitute_criteria(s,profile),profile,{"LANG":self._publang})
    
    def pubdir(self, assembly_dir, profile):
        # calculates and creates the publication directory
        pubdir = self.substitute_criteria(profile.xpath('string(dir/@value)'),profile)
        pubdir = self.substitute_variables(pubdir, profile, {"LANG":self._publang})
        pubdir = assembly_dir + "/" + pubdir + "/" + self._publang
        try:
            self.makedirs(pubdir)
        except:
            logging.debug("publication path %s already exists"%pubdir)
        return pubdir


    def purge_manifest_events(self, pubevents):
        # remove ElementTree objects from events - call before any manifest file update
        if isinstance(pubevents, list):
            map(self.purge_manifest_events, pubevents)
        elif isinstance(pubevents, dict):
            if pubevents.get('ET') is not None:
                pubevents.update({'ET':''})
            map(self.purge_manifest_events, pubevents.values())

class PublisherExtensions(PublisherMixin, AdapterMediawiki, XSLExtensions):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extensions:functions:publication"

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('profile'):
            self._profile = kwargs.get('profile')
            kwargs.pop('profile')
        self.__cache = {}
        super(PublisherExtensions,self).__init__(*args, **kwargs)


    def parse(self, path):
        if not self.__cache.has_key(path):
            self.__cache[path] =  super(PublisherExtensions, self).parse(path)
        return self.__cache[path]
        
    def gettopic(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
        upath = self.getUrlPath(path)
#        logger.debug("get topic %s -> %s"%(modid,upath))
        return upath

    def gettopic2(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
#        logger.debug("get topic path %s -> %s"%(modid,path))
        return path

    def criteria(self, _, *args):
 #       logger.debug('xslt ext criteria')
        criteria = self._profile.xpath("criteria/criterion|/job/criteria/criterion")
        criteria.append(ET.XML('<criterion code="LANG" value="%s"/>'%(self._publang)))
        return criteria

    def criteria_definitions(self, _, *args):
#        logger.debug('xslt ext criteria_definitions')
        return self.project_settings.xpath("/settings/criteria/criterion")

    def lang(self, _, *args):
 #       logger.debug('lang criteria_definitions')
        return self._publang
    
    def normpath(self, _, *args):
        """Returns normalized path"""

        path = args[0]
        try:
            src  = args[1]
            ndir = src.split('/')[:-1]
        except IndexError:
            ndir=[]
        ndir.extend(path.split('/'))
        newdir=[]
        for i in ndir :
            if i=='':
                pass
            if i=='.':
                pass
            if i=='..':
                newdir.pop()
            else:
                newdir.append(i)
        r= '/'.join(newdir)
        return r
        
    def replace_strvar(self, _, args):
        srcstr = self.substitute_criteria(args, self._profile)
        return self.substitute_variables(srcstr, self._profile)

    def replace_criteria(self, _, args):
        srcstr = args
        r = self.substitute_criteria(srcstr, self._profile)
        return r

    def replace_assembly_criteria(self, _, args):
        srcstr = args
        r = self.substitute_criteria(srcstr, self._profile, from_profile=False)
        return r

    def replace_publication_criteria(self, _, args):
        srcstr = args
        r = self.substitute_criteria(srcstr, self._profile)
        return r

    def variable(self, _, *args):
#        logger.debug('variable %s',str(args))
#        logger.debug(ET.tostring(self._profile))
        sheet = self.substitute_criteria(args[0], self._profile)
        variable = self.substitute_criteria(args[1], self._profile)

        # print self.variable_value(sheet, variable, self._profile, {"LANG":self._publang})
        
        return self.variable_value(sheet, variable, self._profile, {"LANG":self._publang})

    def evaluate_condition(self, _, args):
        conditions = args.replace(' ','')
        list_conditions = conditions.split(";")
        return ''
    
    def listdir(self, _, *args):
        path = args[0]
        ext = args[1]        
        try:
            return [os.path.splitext(f['name'])[0] for f in self.get_directory(path) if os.path.splitext(f['name'])[1][1:]==ext]
        except:
            return ["Error: path %s does not exist"%path]

    def upper_case(self, _, *args):
        path = args[0]
        return path.upper()

    def sortable_string(self, _, *args):
        the_string = args[0]
        norm_string = unidecode.unidecode(the_string).upper()
#        logger.debug("norm string %s -> %s"%(the_string, norm_string))        
        return norm_string
    
class ReleasePublisherExtensions(PublisherExtensions):
    def __init__(self, *args, **kwargs):
        if kwargs.has_key('release'):
            self._release = kwargs.get('release')
            kwargs.pop('release')
        super(ReleasePublisherExtensions,self).__init__(*args, **kwargs)

    def process_path(self, path):
        return self._release + '/' + super(ReleasePublisherExtensions, self).process_path(path)
