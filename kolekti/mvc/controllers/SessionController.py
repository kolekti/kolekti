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

""" Session controller"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

# python import

# kolekti imports
from kolekti.http import statuscodes as HS
from kolekti.exceptions import exceptions as EXC

# parent classes

from kolekti.mvc.controllers.PropertiesController import PropertiesController

class SessionController(PropertiesController):
    _model='SessionModel'

    def ctrPROPFIND(self):
        self.__session()
        self.__davheader()
        if self.http.path.startswith('/_session/'):
            super(SessionController,self).ctrPROPFIND()

    def ctrPROPPATCH(self):
        self.__session()
        self.__davheader()
        if self.http.path.startswith('/_session/'):
            super(SessionController,self).ctrPROPPATCH()

    def ctrALL(self):
        self.__session()

    def ctrOPTIONS(self):
        self.__davheader()
        self.http.response.content_type="httpd/unix-directory"
        raise EXC.OK

    def __davheader(self):
        self.http.response.headers.update({"Allow": "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE"})
        self.http.response.headers.update({"DAV": "1"})

    def __session(self):
        sid=self._getdata('session','sid')
        if sid:
            vsid=self.model.validate_session(sid)
        else:
            sid=self.http.cookies.get('KOLEKTISID',None)
            vsid=self.model.validate_session(sid)
        if vsid is not None:
            self._setdata('session','sid',vsid)
            self.http.response.set_cookie('KOLEKTISID',vsid,max_age=360, path='/')
        return vsid
