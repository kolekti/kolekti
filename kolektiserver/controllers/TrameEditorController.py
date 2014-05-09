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



"""controller for trame editor"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.mvc.controllers.DAVController import DAVController
from lxml import etree as ET


class TrameEditorController(DAVController):

    def ctrGET(self):
        if self.model.isCollection(self.http.uri.id):
            super(TrameEditorController, self).ctrGET()
        elif self.model.isResource(self.http.uri.id):
            (data,mime,etag) = self.model.getResource(self.http.uri.id)
            trame=ET.XML(data)

            mods=trame.xpath('//t:module',namespaces={'t':'kolekti:trames'})
            for mod in mods:
                resid=mod.get('resid')
                mod.set('urlid',self.http.uri.hash(resid))
                version=mod.get('version')
                type=mod.get('type')
                p=ET.SubElement(mod,'{kolekti:trames}props')
                if type=='mod':
                    try:
                        p.append(self.model.getpropval(resid,"displayname", "DAV:"))
                        p.append(self.model.getpropval(resid,"title", "kolekti:modules"))
                    except:
                        pass
                if type=="auto":
                    name=ET.SubElement(p,"{kolekti:trames}name")
                    name.text=self.automodules[resid]

            self.http.response.body=ET.tostring(trame).encode('utf-8')
            self.http.response.content_type=mime
            self.http.response.charset="utf-8"
            self._setdata('http', 'etag', etag)
            #self.http.addData(self.model.getpropval(self.http.uri.id, "displayname", "DAV:"))

            self.view.format_resource()

