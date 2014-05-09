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


""" Profile controller"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

# python import

# kolekti imports
from kolekti.http import statuscodes as HS
from kolekti.exceptions import exceptions as EXC

# parent classes

from kolekti.mvc.controllers.PropertiesController import PropertiesController

class ProfileController(PropertiesController):
    _model='ProfileModel'

    def ctrPROPFIND(self):
        self.__davheader()
        if self.http.path.startswith('/_profile/'):
            super(ProfileController,self).ctrPROPFIND()
            raise EXC.OK

    def ctrPROPPATCH(self):
        self.__davheader()
        if self.http.path.startswith('/_profile/'):
            super(ProfileController,self).ctrPROPPATCH()
            raise EXC.OK


    def ctrALL(self):
        pass

    def ctrOPTIONS(self):
        self.__davheader()
        self.http.response.content_type="httpd/unix-directory"
        raise EXC.OK

    def __davheader(self):
        self.http.response.headers.update({"Allow": "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE"})
        self.http.response.headers.update({"DAV": "1"})
