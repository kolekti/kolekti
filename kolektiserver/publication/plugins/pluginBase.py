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

from kolektiserver.kolekticonf import conf
from kolekti.logger import debug

from lxml import etree as ET

class plugin(object):
    _plugin="dummy"
    LOCAL_ENCODING=sys.getfilesystemencoding()
    def __init__(self,publisher, label, suffix, params):
        self.basesdir=conf.get('basedir')
        self.apppath=conf.get('appdir')
        self.publisher=publisher
        self.label=label
        self.suffix=suffix
        self.params=params
        self.conf=conf
        debug ('plugin %s'%self.__module__)
        self.plugindir=os.path.join(self.apppath,'publication','plugins',"_%s"%self.__module__)
        self._plugin=self.__module__

    def get_xsl(self,xslfile):
        xslpath=os.path.join(self.plugindir,'xsl',xslfile)
        return self.publisher.get_xsl(xslpath)

    def postpub(self):
        """
        postpub is the iterator used in plugin
        """
        yield "Dummy plugin"

    def copy_dirfiles(self, srcpath, dstpath, ignore_patterns=(".svn",)):
        """ Copy source path to destination path """
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)
        for lfiles in os.listdir(srcpath):
            newsrcpath = os.path.join(srcpath, lfiles)
            newdstpath = os.path.join(dstpath, lfiles)
            if ignore_patterns.__contains__(lfiles):
                continue
            elif os.path.isdir(newsrcpath):
                if not os.path.exists(newdstpath):
                    os.mkdir(newdstpath)
                self.copy_dirfiles(newsrcpath, newdstpath, ignore_patterns)
            else:
                self.copy_file(newsrcpath, newdstpath)

    def copy_file(self, srcfilepath, dstfilepath):
        """ Copy file source to file destiination """
        shutil.copyfile(srcfilepath, dstfilepath)

    def _load_extensions(self):
        extf_obj = PluginExtension()
        exts = (n for n in dir(PluginExtension) if not(n.startswith('_')))
        self.extensions.update(ET.Extension(extf_obj, exts, ns=extf_obj.ens))

    def _xsl(self,xslfile):
        xsldoc  = ET.parse(xslfile)
        xsl = ET.XSLT(xsldoc, extensions=self.extensions)
        return xsl


class PluginExtension(object):
    ens = "kolekti:extensions:plugin:functions"

    def upper_case(self, _, *args):
        str_ = args[0]
        return str_.upper()
