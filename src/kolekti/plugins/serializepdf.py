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

    def get_command(self):
        import _winreg
        aReg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
        aKey = _winreg.OpenKey(aReg, "SOFTWARE\GPL Ghostscript")
        gsversion = _winreg.EnumKey(aKey, 0)
        sk = _winreg.OpenKey(aKey, gsversion)
        gspaths = _winreg.QueryValueEx(sk,'GS_LIB')
        path = gspaths[0].split(';')[0]
        print 'ghostscript path',path
        return path
    
    def postpub(self):
        """
        main publication function
        """
        res = []
        logging.debug( "serialize pdf  : %s %s"%(self.assembly_dir,self.publication_dir))
        print "serialize pdf",self.assembly_dir,self.publication_dir,self.pivot
        res = self.start_cmd()
        return res
    


