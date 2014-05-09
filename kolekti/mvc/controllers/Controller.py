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




""" MVC controller base class

"""
__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

from kolekti.mvc.MVCFactory import MVCobject,MatchRejected
from kolekti.exceptions import exceptions as EXC
from kolekti.utils.i18n.i18n import tr

class Controller(MVCobject):
    def __init__(self, http):
        super(Controller,self).__init__(http)
        self._register_route_matchers()
        self._getModel()
        self._getView()


    # request matchers :
    def _matcher_method(self, http, match):
        if not match.search(http.method):
            raise MatchRejected


    def _matcher_qs(self, http, match):
        if not match.search(http.path):
            raise MatchRejected

    def _matcher_param(self, http, match, name):
        if not match.search(http.params[name]):
            raise MatchRejected


    def _matcher_header(self, http, match, name):
        if not http.headers.get(name, None):
            raise MatchRejected
        if not match.search(http.headers[name]):
            raise MatchRejected


    def ctrALL(self):
        raise EXC.UnsupportedMethod

    def _getModel(self):
        if hasattr(self,'_model'):
            self.model=self._loadMVCobject_(self._model)
        else:
            self.model=self.http.model

    def _getView(self):
        self.view=self.http.view

    def _setdata(self,namespace,key,value):
        self.http.setdata(namespace,key,value)

    def _setmessage(self, msg, params={}):
        s = tr(msg, params)
        return s.i18n(self.http.translation)

