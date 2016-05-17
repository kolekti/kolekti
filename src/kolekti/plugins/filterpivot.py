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

from kolekti.plugins import pluginBase

class plugin(pluginBase.plugin):
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        logging.debug( "filterpivot  : %s %s"%(self.assembly_dir,self.publication_dir))

        # ouvrir le fichier template
        xslparam = self.get_script_parameter('filter')
        print "*************************",xslparam
        print ET.tostring(self.scriptdef)
        xslt=self.get_xsl(xslparam, profile = self.profile, lang = self._publang)
        puburl=self.getUrlPath(self.publication_plugin_dir)
        # try:
        doc=xslt(self.pivot,
                pubdir=u"'%s'"%puburl,
            )
        res.append({'type':"pivot",
                    "label":"%s_%s"%(self.publication_file,self.scriptname),
#                    "url": "%s/pivot.html"%self.publication_plugin_dir
                    "ET": doc})
        return res
    


