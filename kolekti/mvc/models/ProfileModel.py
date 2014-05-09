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


from kolekti.utils.userdata.userdata import UserData
from kolekti.logger import dbgexc,debug

from kolekti.mvc.models.Properties import Properties
from kolekti.mvc.models.Model import Model

class ProfileModel(Model,Properties):
    __localNS={'kolekti:profile':'kp'}

    def __init__(self, *args, **kwargs):
        Model.__init__(self, *args)
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        Properties.__init__(self, *args , **kwargs)
        self.__userdata=UserData('profils', self.http)

    def isCollection(self, resid):
        return False

#         path=resid.split('/')[1:]
#         return self.__userdata.getKeys(self.http.userId,path) is None

    def isRessource(self, resid):
        return boolean(self.__userdata.getParam(self.http.userId,resid))

    def listCollection(self, resid):
        path=resid.split('/')[1:]
        return self.__userdata.getKeys(self.http.userId,path)

    def _prop_kp_profilevalue(self, resid):
        p = self._xmlprop('profilevalue','kolekti:profile')
        p.text=self.__userdata.getParam(self.http.userId,resid)
        return p

    def _setprop_kp_profilevalue(self, resid, value):
        p = self._xmlprop('profilevalue','kolekti:session')
        self.__userdata.setParam(self.http.userId,resid,value)
        p.text=self.__userdata.getParam(self.http.userId,resid)
        return p

    def _delprop_kp_profilevalue(self, resid):
        p = self._xmlprop('profilevalue','kolekti:session')
        self.__userdata.delete(self.http.userId,resid)
        return p

