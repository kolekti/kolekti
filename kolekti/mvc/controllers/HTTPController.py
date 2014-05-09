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




""" HTTP basic controller"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc,debug

from kolekti.mvc.controllers.Controller import Controller
class HTTPController(Controller):

    def ctrGET(self):
        resid=self.model.resid
        if self.model.isResource(resid):
            # returns the raw resource
            (data,mime,etag) = self.model.getResource(resid)
            self._setdata('http','body',data)
            self._setdata('http','mime',mime[0])
            self._setdata('http','etag',etag)
            self.view.format_resource()
        elif self.model.isCollection(resid):
            #lists the collection and call the view to format it
            dirs = self.model.listCollection(resid)
            dirlist=[]
            for d in dirs:
                if self.model.isCollection(resid+u"/"+d):
                    dirlist.append(d+"/")
                else:
                    dirlist.append(d)
            self._setdata('http','listdir',dirlist)
            self.view.format_collection()
        else:
            raise EXC.NotFound()

        self.http.response.cache_expires(seconds=3600)
        raise EXC.OK
