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



""" Factory for import controllers on demand """

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''


from kolekti.mvc.MVCFactory import MVCFactory

class ControllerFactory(MVCFactory):
    def getController(self, http):
        ctrName = self._getObject('controller', http)
        ctr=self._loadMVCobject_(ctrName,http)
        return ctr

    def getControllers(self, http):
        for c in self._getObjects('controller', http):
            ctr=self._loadMVCobject_(c,http)
            yield ctr

