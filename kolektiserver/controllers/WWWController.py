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



"""controller for modules"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.exceptions import exceptions as EXC
from kolekti.mvc.controllers.DAVController import DAVController

class WWWController(DAVController):

    def ctrGET(self):
        if self.http.path == '/':
            res = self.model.getProjectsList()
            self._setdata('http', 'body', res)
            self.view.format_collection()

        elif self.model.isResource(self.http.path):
            (data,mime,etag) = self.model.getResource(self.http.path)
            self._setdata('http', 'body', data)
            self._setdata('http', 'mime', mime[0])
            self._setdata('http', 'etag', etag)
            self.view.format_resource()

        elif self.model.isCollection(self.http.path):
            res = self.model.getCollection(self.http.path)
            self._setdata('http', 'body', res[0])
            self.view.format_collection()
        else:
            raise EXC.NotFound()
        raise EXC.OK()
