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

""" XSLT+UI generator based view base class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''
import os
from lxml import etree as ET

from kolekti.kolekticonf import conf
from kolekti.logger import debug,dbgexc

from kolekti.mvc.views.XSLView import XSLView

# Default View Class, all other view classes derivate from this one
class XSLUIView(XSLView):

    def __init__(self, http):
        super(XSLUIView,self).__init__(http)

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
            d = self._dialogs(r)
            l = self._localize(d)
            return self._serialize(l)
        except ET.XSLTApplyError, e:
            debug( xsl.error_log )
            dbgexc()
            return xsl.error_log

    def _dialogs(self, doc):
        xslfile = os.path.join(conf.get('fmkdir'),'utils', 'ui', 'xsl', 'dialogs.xsl')
        xsl  = self._xsl(xslfile)
        return xsl(doc, kolektiapp="'%s'" % conf.get('appdir'), kolektifmk="'%s'" % conf.get('fmkdir'))

