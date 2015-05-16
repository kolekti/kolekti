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
import json
from lxml import etree as ET

from common import kolektiBase, XSLExtensions, LOCAL_ENCODING



class PublisherMixin(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}
    def __init__(self, *args, **kwargs):
        # intercept lang & draft parameters

        self._publang = None
        if kwargs.has_key('lang'):
            self._publang = kwargs.get('lang')
            kwargs.pop('lang')

        self._draft = False
    
        super(PublisherMixin, self).__init__(*args, **kwargs)

        if self._publang is None:
            self._publang = self._config.get("sourcelang","en")

                        
    def process_path(self, path):
        return self.substitute_criteria(path, ET.XML('<criteria/>'))

    def substitute_criteria(self, string, profile, extra={}):
        extra.update({"LANG":self._publang})
        return super(PublisherMixin, self).substitute_criteria(string, profile, extra=extra)

    
    def pubdir(self, assembly_dir, profile):
        # calculates and creates the publication directory
        pubdir = self.substitute_variables(profile.xpath('string(dir/@value)'),profile)
        pubdir = self.substitute_criteria(pubdir, profile)
        pubdir = assembly_dir + "/publications/" + pubdir
        logging.debug('pubdir : %s'%pubdir)

        try:
            self.makedirs(pubdir)
        except:
            logging.debug("publication path %s already exists"%pubdir)
        return pubdir
    
class PublisherExtensions(PublisherMixin, XSLExtensions):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extensions:functions:publication"

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('profile'):
            self._profile = kwargs.get('profile')
            kwargs.pop('profile')
        super(PublisherExtensions,self).__init__(*args, **kwargs)
        

    def gettopic(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
        upath = self.getUrlPath(path)
        logging.debug("get topic %s -> %s"%(modid,upath))
        return upath

    def gettopic2(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
        logging.debug("get topic path %s -> %s"%(modid,path))
        return path

    def criteria(self, _, *args):
        logging.debug('xslt ext criteria')
        return self._profile.xpath("criteria/criterion|/job/criteria/criterion")

    def criteria_definitions(self, _, *args):
        logging.debug('xslt ext criteria_definitions')
        return self._project_settings.xpath("/settings/criteria/criterion")

    def lang(self, _, *args):
        logging.debug('lang criteria_definitions')
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

    def variable(self, _, *args):
        sheet = self.substitute_criteria(args[0], self._profile)
        variable = self.substitute_criteria(args[1], self._profile)
        return unicode(self.variable_value(sheet, variable, self._profile, {"LANG":self._publang}))

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
