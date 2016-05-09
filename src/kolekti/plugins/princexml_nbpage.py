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

from lxml import etree as ET
from PyPDF2 import PdfFileReader

from kolekti.plugins import pluginBase

class plugin(pluginBase.plugin):
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        pivot = self.pivot
        body = pivot.xpath('/*/*[local-name() = "body"]')[0]

        # make image urls relative in pivot
        for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
            src = media.get('src')
            if src[0] == "/":
                media.set('src', src[1:])

        logging.debug( "pdf nbpages : %s %s"%(self.assembly_dir,self.publication_dir))

        # produce pdf once
        first_res = self.start_cmd()
        pdf = first_res[0]['file']

        # count pages in pdf
        with open(self.getOsPath(pdf), 'rb') as pdf:
            nbpages = PdfFileReader(pdf).getNumPages() 

        # update pivot body attributes
        body.set('data-nbp', str(nbpages))
        body.set('data-nbp2', str(nbpages % 2))
        body.set('data-nbp4', str(nbpages % 4))
        body.set('data-nbp8', str(nbpages % 8))
        body.set('data-nbp16', str(nbpages % 16))

        # produce pdf with modified pivot
        res = self.start_cmd()
        
        return res
    


