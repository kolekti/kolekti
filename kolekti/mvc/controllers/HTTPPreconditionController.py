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




""" this controller checks ifMatch header in an http request"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

from kolekti.exceptions import exceptions as EXC
from kolekti.mvc.controllers.Controller import Controller
from kolekti.logger import dbgexc,debug


class HTTPPreconditionController(Controller):

    def ctrALL(self):
        pass

    def ctrPROPFIND(self):
        context=self.http.headers.get('KolektiContext',None)
        if context is not None:
            try:
                etag = self.model.getEtag(self.http.path)
                self.http.response.headers.update({'ETag':'"%s"'%etag})
            except:
                etag = None

            if etag in self.http.if_none_match:
                raise EXC.NotModified

    def ctrPUT(self):
        try:
            etag = self.model.getEtag(self.http.path)
            self.http.response.headers.update({'ETag':'"%s"'%etag})
        except:
            dbgexc()

            etag = None

        if etag in self.http.if_none_match:
            #return a 304
            raise EXC.PreconditionFailed

        try:
            modif_date=self.model.getprop("DAV:modifdate")
            if req.if_modified_since and req.if_modified_since >= modif_date:
               raise EXC.PreconditionFailed
        except:
            pass

        return

        self.http.IfNoneMatch
        if self.http.IfMatch is not None:
            if self.http.IfMatch=="*":
                if etag is None:
                    raise EXC.PreconditionFailed
            else:
                if not etag in self.http.IfMatch:
                    raise EXC.PreconditionFailed

        if etag is not None and self.http.IfNoneMatch is not None:
            if self.http.IfNoneMatch=="*":
                raise EXC.PreconditionFailed
            if etag in self.http.IfNoneMatch:
                if self.http.method=="GET" or self.http.method=="HEAD":
                    self.http.response.setHeader('ETag','"%s"'%etag)
                    raise EXC.NotModified
                else:
                    raise EXC.PreconditionFailed
