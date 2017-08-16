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


import os
import time
import shutil
import logging
logger = logging.getLogger(__name__)

from lxml import etree as ET
from PyPDF2 import PdfFileReader

from kolekti.plugins import pluginBase
from weasyprint import HTML

class plugin(pluginBase.plugin):
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        pivot = self.pivot
        body = pivot.xpath('/*/*[local-name() = "body"]')[0]
        head = pivot.xpath('/*/*[local-name() = "head"]')[0]

        # add css
        css = self.scriptdef.xpath('string(parameters/parameter[@name="CSS"]/@value)')
        logger.debug(css)
        baseurl = "file://%s"%(self.getOsPath("/"))
        csslink = "%s/kolekti/publication-templates/weasyprint/css/%s.css"%(baseurl,css)
 
        logger.debug(csslink)
        ET.SubElement(head,'link',attrib = {
            "rel":"stylesheet",
            "type":"text/css",
            "href": csslink
            })
        ET.SubElement(head,'base',attrib = {
            "href": baseurl
            })
        
       
        # make image urls relative in pivot
        for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
            src = media.get('src')
            if src[0] == "/":
                media.set('src', src[1:])


        # produce pdf once
        pubdir = self.pubdir(self.assembly_dir, self.profile)        
        pdf = os.path.join(self.getOsPath(pubdir),self.publication_file+'.pdf')
        
        HTML(string = ET.tostring(pivot)).write_pdf(pdf)

        if self.scriptdef.xpath('boolean(parameters/parameter[@name="two_passes"]/@value = "yes")'):
            # count pages in pdf
            with open(pdf, 'rb') as pdffile:
                nbpages = PdfFileReader(pdffile).getNumPages() 
                
            logger.debug( "pdf nbpages : %d"%(nbpages,))
    
            # update pivot body attributes
            body.set('data-pagecount', str(nbpages))
            body.set('data-pagecount-mod-2', str(nbpages % 2))
            body.set('data-pagecount-mod-4', str(nbpages % 4))
            body.set('data-pagecount-mod-8', str(nbpages % 8))
            body.set('data-pagecount-mod-16', str(nbpages % 16))


            pivfile = pubdir + "/document_nbpage_attrs.xhtml"
            self.xwrite(pivot, pivfile, sync = False)
            
            # produce pdf with modified pivot
            HTML(string = ET.tostring(pivot)).write_pdf(pdf)

        subst = {}
        for p in self.scriptdef.xpath('parameters/parameter'):
            subst.update({p.get('name'):p.get('value')})
                
        pubdir = self.pubdir(self.assembly_dir, self.profile)
        subst.update({
            "APPDIR":self._appdir,
            "PLUGINDIR":self._plugindir,
            "PUBDIR":self.getOsPath(pubdir),
            "SRCDIR":self.getOsPath(self.assembly_dir),
            "BASEURI":self.getUrlPath(self.assembly_dir) + '/',
            "PUBURI":pubdir,
            "PUBNAME":self.publication_file,
        })
        xl=self.scriptspec.find('link')
        outfile=self._substscript(xl.get('name'), subst, self.profile)
        outref=self._substscript(xl.get('ref'), subst, self.profile)
        outtype=xl.get('type')

        res=[{"type":outtype, "label":outfile, "url":outref, "file":outref}]
        return res
    


