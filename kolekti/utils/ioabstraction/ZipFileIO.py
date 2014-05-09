# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
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
import zipfile

from StringIO import StringIO
from lxml import etree as ET

from kolekti.kolekticonf import conf
from kolekti.logger import debug,dbgexc

class ZipFileIO(object):
    def __init__(self, http):
        self.http=http

    @property
    def zipfile(self):
        return self.__zipfile

    def open(self, path=None, mode='w', data=None):
        assert path!=None or data!=None or mode=='w', "Trying to read zip without a file"

        if path is None and not data is None:
            self.__zipfile = StringIO(data)
            self.__zipobj = zipfile.ZipFile(self.__zipfile,mode)
        else:
            self.__zipfile = path
            self.__zipobj = zipfile.ZipFile(path,mode)

    def write(self, path, arcname=""):
        if arcname == "":
            arcname = path
        self.__zipobj.write(path, arcname)

    def writestr(self, path, bytes=""):
        self.__zipobj.writestr(path, bytes)

    def read(self, path):
        return self.__zipobj.read(path)

    def getinfo(self, path):
        return self.__zipobj.getinfo(path)

    def infolist(self):
        return self.__zipobj.infolist()

    def namelist(self):
        return self.__zipobj.namelist()

    def close(self):
        self.__zipobj.close()
