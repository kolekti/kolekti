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
from kolekti.publish_utils import PublisherMixin, PublisherExtensions

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
        self.scriptname = scriptdef.get('name')
        logging.debug("calling script %s", self.scriptname)
        self.scriptdef = scriptdef
        self.profile = profile
        self.assembly_dir = assembly_dir
        self.pivot = pivot
        self.lang = lang
        pubfile = scriptdef.xpath('string(filename)')
        pubfile = self.substitute_variables(pubfile, profile)
        self.publication_file = self.substitute_criteria(pubfile, profile)

        self.publication_dir = self.pubdir(assembly_dir, profile)
        self.publication_plugin_dir = self.publication_dir+"/"+ self.publication_file + "_" + self.scriptname
        try:
            self.makedirs(self.publication_plugin_dir)
        except:
            pass
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
        # copy media from assembly space source to publication directory
        for med in self.pivot.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):

            ref = med.get('src')
            ref = self.substitute_criteria(ref, self.profile)
            try:
                refdir = "/".join([self.publication_plugin_dir]+ref.split('/')[:-1])
                self.makedirs(refdir)
            except OSError:
                logging.debug('makedir failed')
                import traceback
                logging.debug(traceback.format_exc())

            self.copyFile("/".join([self.assembly_dir,ref]), "/".join([self.publication_plugin_dir,ref]) )

        # copy plugin lib from assembly space to publication directory
        label = self.scriptdef.get('name')
        ass_libdir = '/'.join([self.assembly_dir,'kolekti','publication-templates',label,'lib'])
        self.copyDirs(ass_libdir, self.publication_plugin_dir + '/lib')
        
    def postpub(self):
        """
        postpub is the iterator used in plugin
        """
        logging.debug('Dummy plugin')
        return "Dummy plugin"

    def get_script_parameter(self, param):
        try:
            return self.scriptdef.xpath('string(./parameters/parameter[@name="%s"]/@value)'%param)
        except:
            import traceback
            logging.error("Unable to read script parameters: %s"%param)
            logging.debug(traceback.format_exc())
            return None
