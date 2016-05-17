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

# ExportPublicationToFolder

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
        # logger.debug( "WebHelp5  : %s %s"%(self.assembly_dir,self.publication_dir))

        # copy libs from assembly space to publication directory
        dst = self.get_script_parameter('destination')
        for item in self.input:
            if 'ET' in item.keys():
                logger.debug( "pass ET %s"% item.type)

            elif item.get('type','') == "directory":
                pathparts = os.path.split(item['path'])
                srcdn = pathparts[-1]
                if srcdn == "":
                    srcdn = pathparts[-2]

                src = self.getOsPath(item['path'])
                self.__mkdir(dst)
                try:
                    shutil.rmtree(os.path.join(dst,srcdn))
                except:
                    # import traceback
                    # print traceback.format_exc()
                    pass
                shutil.copytree(src, os.path.join(dst,srcdn))
                logger.debug("copy plugin directory %s to %s"%(src,dst))

            elif 'file' in item.keys():
                self.__mkdir(dst)
                src = self.getOsPath(item['file'])
                srcfn = os.path.basename(src)
                shutil.copyfile(src, os.path.join(dst, srcfn))
                logger.debug( "copy plugin file %s to %s"%(src,dst))

            return self.input

    def __mkdir(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                # import traceback
                # print traceback.format_exc()
                pass
