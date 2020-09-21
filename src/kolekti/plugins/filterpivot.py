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

from kolekti.plugins import pluginBase

class plugin(pluginBase.plugin):
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        logger.debug( "filterpivot  : %s %s"%(self.assembly_dir,self.publication_dir))

        # ouvrir le fichier template
        xslfilter = self.get_script_parameter('filter')
        xslparams = self.get_script_parameter('filter_parameters')
        try:
            xsl_parameters = eval(xslparams)
        except:
            logger.warning('Error evaluating filter_parameters')
            xsl_parameters = {}
        xslt=self.get_xsl(xslfilter, profile = self.profile, lang = self._publang)
        puburl=self.getUrlPath(self.publication_plugin_dir)
        # try:
        rooturl = self.getUrlPath(self.process_path('/'))
        logger.debug( "filter parameters  : %s"%str(xsl_parameters))
        doc=xslt(self.pivot,
                 pubdir=u"'%s'"%puburl,
                 rootdir=u"'%s'"%rooturl,
                 **xsl_parameters
        )        
        for entry in xslt.error_log:
            logger.debug("xsl> ", entry.message)
                    
        res.append({'type':"pivot",
                    "label":"%s_%s"%(self.publication_file,self.scriptname),
#                    "url": "%s/pivot.html"%self.publication_plugin_dir
                    "ET": doc})
        return res
    


