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


import pluginBase
import os
import shutil
import time
import base64

import logging
logger = logging.getLogger(__name__)


from lxml import etree as ET
htmlns="http://www.w3.org/1999/xhtml"

class plugin(pluginBase.plugin):
    def postpub(self):
        pubdir = self.pubdir(self.assembly_dir, self.profile)
        res = []

        pivot = self.pivot
        doctitle = pivot.xpath('string(/h:html/h:head/h:title)', namespaces=self.nsmap)
        html = pivot.getroot()
        
        # suppression des div topicinfo
        for div in pivot.xpath("//h:div[@class='topicinfo']", namespaces=self.nsmap):
            div.getparent().remove(div)

        
        # remplacement du <head>
        head = ET.Element('{%s}head'%self.nsmap['h'])
        html.remove(html.find('h:head', namespaces=self.nsmap))
        html.insert(0, head)

        # insertion de la feuille de style (parametre css du script)
        meta = ET.SubElement(head, '{%s}meta'%self.nsmap['h'], {
            'content': 'application/xhtml+xml; charset=UTF-8',
            'http-equiv': 'content-type'})
        
        title = ET.SubElement(head, '{%s}title'%self.nsmap['h'])
        title.text = doctitle
        
        css = self.get_script_parameter('CSS')
        logger.debug(css)        
        if css is not None and len(css):
            csspath = '/'.join([self.assembly_dir,'kolekti','publication-templates','html_autonome','css', css + '.css'])
            logger.debug(csspath)
            style = ET.SubElement(head, '{%s}style'%self.nsmap['h'])        
            with open(self.getOsPath(csspath)) as f:
                style.text = f.read()

        
        # remplace les attribut src des images par leur équivalient en base64
        for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
            src = media.get('src')
            img_type = os.path.splitext(src)[1][1:]                        
            with open(self.getOsPath(src)) as f:
                data = base64.encodestring(f.read())
            media.set('src', 'data:image/' + img_type + ';base64,' + data)
        filename="%s.html" %(self.publication_file,)
        top = self.getOsPath(self.publication_plugin_dir)
        hf=os.path.join(self.getOsPath(self.publication_dir), filename)
        with open(hf,"w") as f:
            f.write(str(pivot))
        logger.debug( "html autonome  : %s"%(hf,))
        res.append({'type':"pivot",
                    'url':"%s/%s"%(self.publication_dir, filename),
                    "label":filename,
                    "ET": pivot})
        
        return res
