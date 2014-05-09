# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


""" XSLT based view base class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''
import os
from lxml import etree as ET
from webob.exc import *

from kolekti.kolekticonf import conf
from kolekti.exceptions import exceptions as EXC
from kolekti.http import statuscodes as HS
from kolekti.logger import debug,dbgexc

from kolekti.mvc.views.View import View
from kolekti.mvc.views import XSLExtensions

class ViewXSLExtensions(XSLExtensions.KFunctions):
    pass

class KolektiPrefixResolver(ET.Resolver):
    """ lxml url resolver for kolekti:// url """
    prefix='kolekti'

    def resolve(self, url, pubid, context):
        if url.startswith('kolekti://'):
            localpath=url.split('/') [2:]
            return self.resolve_filename(os.path.join(conf.get('fmkdir'), *localpath),context)
        if url.startswith('kolektiapp://'):
            localpath=url.split('/') [2:]
            return self.resolve_filename(os.path.join(conf.get('appdir'), *localpath),context)

# Default View Class, all other view classes derivate from this one
class XSLView(View):
    _urlresolver=KolektiPrefixResolver()
    def __init__(self, http):
        super(XSLView,self).__init__(http)
        self.extensions = {}
        self._load_extensions()
        # extension functions

    def _load_extensions(self):
        extf_obj = ViewXSLExtensions(self.http, self.model)
        exts = (n for n in dir(ViewXSLExtensions) if not(n.startswith('_')))
        self.extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))


    def _xsl(self,xslfile):
        parser = ET.XMLParser()
        parser.resolvers.add(self._urlresolver)
        xsldoc  = ET.parse(xslfile,parser)
        xsl = ET.XSLT(xsldoc, extensions=self.extensions)
        return xsl

    def format_collection(self):
        xslf='%s.xsl' % self.__module__
        xslfile = os.path.join(conf.get('appdir'),'views', 'xsl', xslf)
        xsl  = self._xsl(xslfile)
        try:
            r = xsl(self.http.xml)
            l = self._localize(r)
            return self._serialize(l)
        except ET.XSLTApplyError, e:
            debug( xsl.error_log )
            raise EXC.Error(HS.STATUS_CODES[500], xsl.error_log)

    def format_properties(self, response):
        xslf='%s_properties.xsl' % self.__module__
        xslfile = os.path.join(conf.get('appdir'),'views', 'xsl', xslf)
        xsl = self._xsl(xslfile)
        try:
            r = xsl(ET.XML(response))
            l = self._localize(r)
            response = ET.tostring(l)
        except ET.XSLTApplyError, e:
            debug( xsl.error_log )
            raise EXC.Error(HS.STATUS_CODES[500], xsl.error_log)

        return response

    def _localize(self, doc):
        xslfile = os.path.join(conf.get('fmkdir'),'utils', 'i18n', 'xsl', 'i18n.xsl')
        xsl = self._xsl(xslfile)
        return xsl(doc)
    
    def _serialize(self, r):
        self.http.response.body=ET.tounicode(r, pretty_print='yes').encode('utf-8')
        self.http.response.content_type="text/html"
        self.http.response.charset="utf-8"

    def error(self, code, msg, stack=""):

        res = """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">"""

        res = res + "<head>"
        res = res + "<title>Kolekti</title>"
        res = res + "<link rel='stylesheet' type='text/css' href='/_lib/css/kolekti_error.css'/>"
        res = res + "</head>"
        res = res + "<body>"
        res = res + "<h1>Error %s : %s</h1>" % (str(code), HS.STATUS_CODES[code])
        res = res + "<div id=\"message\">"
        res = res + msg
        res = res + "</div>"
        if code == 500:
            res = res + "<div id=\"stack\"><pre>"
            res = res + stack
            res = res + "</pre></div>"
        res = res + "</body></html>"

        self.http.response.status=code
        if code == 401:
            self.http.response.status=401

        self.http.response.body=res.encode('utf-8')
        self.http.response.content_type="text/html"
        self.http.response.charset="utf-8"

    def applicationerror(self, code, msg, stack=""):
        self.error(code, msg, stack)
