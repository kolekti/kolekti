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



""" MVC controller returning iterator class

"""
from kolekti.exceptions import exceptions as EXC
from kolekti.mvc.controllers.Controller import Controller

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''
class IterController(Controller):

    def ctrGET(self):
        self.http.response.app_iter=self.genGET()
        raise EXC.OK

    def ctrPOST(self):
        self.http.response.app_iter=self.genPOST()
        raise EXC.OK

    def ctrALL(self):
        pass
