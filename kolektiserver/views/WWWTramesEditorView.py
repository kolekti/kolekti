# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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


"""
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
from lxml import etree as ET

from kolekti.exceptions import exceptions as EXC
from kolekti.http import statuscodes as HS
from kolekti.logger import debug
from kolekti.utils.i18n.i18n import tr

from kolektiserver.kolekticonf import conf
from kolektiserver.views.WWWView import WWWView

class WWWTramesEditorView (WWWView):
    __automodules={"kolekti://TDM":u"[0076]Table des matières",
                 "kolekti://INDEX":u"[0077]Index",
                 "kolekti://REVNOTES":u"[0343]Table des modifications"}

    def format_resource(self):
        xslf='%s.xsl' % self.__module__
        xslfile = os.path.join(conf.get('appdir'),'views', 'xsl', xslf)
        xsl  = self._xsl(xslfile)
        data = self._getdata('http', 'body')
        if not ET.iselement(data):
            xml = ET.XML(data)
        else:
            xml = data
        mods=xml.xpath('//t:module',namespaces={'t':'kolekti:trames'})
        for mod in mods:
            resid=unicode(mod.get('resid'))
            mod.set('urlid',self.http.urlhash)
            type=mod.get('type')
            p=ET.SubElement(mod,'{kolekti:trames}props')
            if type=='mod':
                try:
                    self._get_module_props(p,resid)
                except:
                    pass
            if type=="auto":
                name=ET.SubElement(p,"{kolekti:trames}name")
                s = tr(self.__automodules[resid])
                name.text = s.i18n(self.http.translation)
        try:
            r = xsl(xml)
            l = self._localize(r)
            self._serialize(l)
        except ET.XSLTApplyError, e:
            debug( xsl.error_log )
            raise EXC.Error(HS.STATUS_CODES[500], xsl.error_log)

    def _get_module_props(self,p,resid):
        MM=self._loadMVCobject_('ModulesModel')
        p.append(MM.getpropval(resid,"displayname", "DAV:"))
        #p.append(MM.getpropval(resid,"title", "kolekti:modules"))
