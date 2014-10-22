# -*- coding: utf-8 -*-
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
import sys
import shutil
import logging
from lxml import etree as ET
from kolekti.common import kolektiBase
from kolekti.publish import PublisherMixin, PublisherExtensions

class PluginsExtensions(PublisherExtensions):
    def __init__(self, *args, **kwargs):
        self._resdir = "."
        if kwargs.has_key('resdir'):
            self._resdir = kwargs.get('resdir')
            kwargs.pop('resdir')
        super(PluginsExtensions,self).__init__(*args, **kwargs)

    def process_path(self, path):
        return self._resdir + "/" +super(PluginsExtensions, self).process_path(path)
    
    

class plugin(PublisherMixin,kolektiBase):
    _plugin="dummy"
    LOCAL_ENCODING=sys.getfilesystemencoding()
    
    def __init__(self, *args, **kwargs):
        super(plugin, self).__init__(*args, **kwargs)
        self._plugin = self.__module__.split('.')[-1]
        self._plugindir = os.path.join(self._appdir,'plugins',"_%s"%self._plugin)
        self.__ext = PluginsExtensions
        logging.debug("*********** init plugin with extension %s"%self.__ext)
        
    def get_xsl(self,xslfile, **kwargs):
        logging.debug("get xsl from plugin %s"%self._plugindir)
        return super(plugin,self).get_xsl(xslfile, extclass = self.__ext,
                                          xsldir = self._plugindir,
                                          system_path = True,
                                          resdir = self.assembly_dir,
                                          **kwargs)

    def __call__(self, scriptdef, profile, assembly_dir, pivot, lang ):
        self.scriptdef = scriptdef
        self.profile = profile
        self.assembly_dir = assembly_dir
        self.pivot = pivot
        self.lang = lang
        
        scriptlabel = scriptdef.get('name')
        profilelabel = profile.xpath('string(label)')
        logging.debug("calling script ", scriptlabel)
                
        self.publication_dir = self.pubdir(assembly_dir, profile) + "/" + scriptlabel

        try:
            self.makedirs(self.publication_dir)
        except:
            logging.debug("publication path %s already exists"%self.publication_dir)            
        
        return self.postpub()

    def copylibs(self, assembly_dir, label):
        # copy libs from plugin directory to assembly space
        libsdir = os.path.join(self._plugindir,'lib')
        if os.path.exists(libsdir):
            libpdir = os.path.join(self.getOsPath('/'.join([assembly_dir,'kolekti','publication-templates',label])), 'lib')
            try:
                shutil.rmtree(libpdir)
            except:           
                pass
            shutil.copytree(libsdir, libpdir)


    def copymedias(self):
        for d in ['sources']:
            source = self.assembly_dir + '/' + d
            target = self.publication_dir + '/' + d
            if self.exists(source):
                self.copyDirs(source,target)
            
    def postpub(self):
        """
        postpub is the iterator used in plugin
        """
        return "Dummy plugin"

    def get_script_parameter(self, param):
        try:
            return self.scriptdef.xpath('string(./parameters/parameter[@name="%s"]/@value)'%param)
        except:
            import traceback
            logging.error("Unable to read script parameters: %s"%param)
            logging.debug(traceback.format_exc())
            return None
