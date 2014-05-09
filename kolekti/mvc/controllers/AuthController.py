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




""" Performs Basic HTTP Authentification """

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import base64

from kolekti.exceptions import exceptions as EXC
from kolekti.mvc.controllers.Controller import Controller
from kolekti.kolekticonf import conf
from kolekti.logger import dbgexc,debug


class AuthController(Controller):
    try:
        _model=conf.get('authmodel')
    except KeyError:
        _model='AuthModel'

    # routing matchers
    def _matcher_user(self,http,public):
        public=int(public)
        try:
            if public==0 and http.getdata('auth','uid')==0:
                raise MatchRejected
        except AttributeError:
            raise MatchRejected

    def _matcher_group(self,http,clearance):
        try:
            if http.getdata('auth','uid')==0:
                raise MatchRejected
            if not clearance in http.getdata('auth','clearances'):
                raise MatchRejected
        except AttributeError:
            raise MatchRejected

    def ctrALL(self):
        # get Authorisation header
        auth = self.http.headers.get('AUTHORIZATION', None)
        if not auth or self.http.headers['AUTHORIZATION'].find('Basic') == -1:
            raise EXC.AuthError
        token = auth.split(' ')[1]

        # decode the auth token
        authstring = base64.decodestring(token).split(':')
        login    = authstring[0].decode('iso-8859-1')
        password = authstring[1].decode('iso-8859-1')

        # check authentication
        uid = self.model.authenticate(login,password)
        self.set_user_info(uid)
            
    def set_user_info(self, uid):
        user = self.model.user(uid)
        self._setdata('user','locale',user.lang)
        self._setdata('user','timezone',user.timezone)
        self._setdata('auth','uid',uid)
        if user.is_translator:
            clearances = ["translator"]
        else:
            clearances = ["user"]
        if user.is_admin:
            clearances.append("admin")
        self._setdata('auth','clearances', clearances)
