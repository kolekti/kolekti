# -*- coding: utf-8 -*-
#
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

""" view base class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import lxml.etree as ET

from kolekti.http import statuscodes as HS
from kolekti.mvc.MVCFactory import MVCobject

#Default View Class, all other view classes derivate from this one
class View(MVCobject):

    def __init__(self, http):
        super(View,self).__init__(http)
        self.model=self.http.model

    def generateResourceDisplayPage(self):
        return

    def format_collection(self):
        self.http.response.body=self._getdata('http','listdir')
        self.http.response.content_type="text/plain"

    def format_resource(self):
        data = self._getdata('http','body')
        if ET.iselement(data):
            data = ET.tostring(data)
        self.http.response.body=data
        try:
            self.http.response.content_type=self._getdata('http','mime')
        except TypeError:
            self.http.response.content_type="application/data"

    def format_properties(self, response):
        return response

    def error(self, code, msg, stack=""):
        res = "Error %s : %s\n" % (str(code), HS.STATUS_CODES[code])
        res = res + msg
        if code == 500:
            res = res + "\n"
            res = res + stack
        self.http.response.status=code
        self.http.response.body=res.encode('utf-8')
        self.http.response.content_type="text/plain"
        self.http.response.charset="utf-8"
