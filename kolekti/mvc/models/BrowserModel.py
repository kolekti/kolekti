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




""" model : Browser class, based on DEV model, implements sproperties specific to
            kolekti ajax browser
"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import hashlib
from kolekti.mvc.models.SessionModel import SessionModel
from kolekti.mvc.models.DAVModel import DAVModel
from kolekti.logger import dbgexc,debug


class BrowserModel(DAVModel):
    __localNS={'kolekti':'k',
               "kolekti:usersession":"ku"}

    def __init__(self, *args, **kwargs):
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(BrowserModel,self).__init__(*args,**kwargs)
        self.session = SessionModel(*args, **kwargs)

    #Kolekti specific Properties

    def _prop_k_writable(self, resid):
        p = self._xmlprop('writable','kolekti')
        #p.text = uri.objname
        p.text = 'yes'
        return p

    def _prop_k_resourceid(self, resid):
        p = self._xmlprop('resourceid','kolekti')
        #p.text = uri.objname
        m = hashlib.md5()
        m.update(resid.encode('utf-8'))
        p.text = m.hexdigest()
        return p

    def _prop_k_resid(self, resid):
        p = self._xmlprop('resid','kolekti')
        #p.text = uri.objname
        p.text = resid
        return p

    # Session
    def _prop_ku_dirstate(self, resid):
        ''' Define state of dir '''
        browserid=self.http.headers.get('KolektiBrowser','')
        p = self._xmlprop('dirstate','kolekti:usersession')
        key=":".join((self.http.sessionId,resid,browserid))
        p.text=self.session.userdata.getParam(self.http.userId, key)
        return p

    def _setprop_ku_dirstate(self, resid, value):
        browserid=self.http.headers.get('KolektiBrowser','')
        p = self._xmlprop('dirstate','kolekti:usersession')
        key=":".join((self.http.sessionId,resid,browserid))
        self.session.userdata.setParam(self.http.userId, key,value)
        p.text=self.session.userdata.getParam(self.http.userId, key)
        return p

