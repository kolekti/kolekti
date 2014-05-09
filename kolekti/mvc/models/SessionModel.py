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




""" model : Sessions, use SessionService"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import uuid

from kolekti.utils.userdata.userdata import UserData
from kolekti.logger import dbgexc,debug

from kolekti.mvc.models.Properties import Properties
from kolekti.mvc.models.Model import Model

class SessionModel(Model,Properties):
    __localNS={'kolekti:session':'ks'}

    def __init__(self, *args, **kwargs):
        Model.__init__(self, *args)
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        Properties.__init__(self, *args, **kwargs)
        self.__userdata=UserData('session', self.http)

    @property
    def userdata(self):
        return self.__userdata

    def validate_session(self,sid=None):
        if sid is None:
            sid = self._getdata('session', 'sid')
        sid=self.getSession(self.http.userId,sid)
        return sid

    def isCollection(self, resid):
        return False

    def isRessource(self, resid):
        sid=self.validate_session()
        return boolean(self.__userdata.getParam(sid,resid))

    def listCollection(self, resid):
        return []

    def _prop_ks_sessionvalue(self, resid):
        p = self._xmlprop('sessionvalue','kolekti:session')
        sid=self.validate_session()
        key=':'.join((sid,resid))
        value=self.__userdata.getParam(self.http.userId, key)
        try:
            p.append(value)
        except TypeError:
            p.text=value
        return p

    def _setprop_ks_sessionvalue(self, resid, value):
        p = self._xmlprop('sessionvalue','kolekti:session')
        sid=self.validate_session()
        path=resid.split('/')[2:]
        key=':'.join((sid,resid))
        self.__userdata.setParam(self.http.userId, key, value)
        value=self.__userdata.getParam(self.http.userId, key)
        try:
            p.append(value)
        except TypeError:
            p.text=value
        return p

    def _delprop_ks_sessionvalue(self, resid):
        p = self._xmlprop('sessionvalue','kolekti:session')
        sid=self.validate_session()
        key=':'.join((sid,resid))
        self.__userdata.delete(self.http.userId, key)
        return p

    def getSession(self, uid, sessionkey=None):
        if sessionkey is None:
            sessionkey=str(uuid.uuid4())
            self.__userdata.setParam(uid,sessionkey,True)
            return sessionkey
        elif self.__userdata.getParam(uid,sessionkey):
            return sessionkey

