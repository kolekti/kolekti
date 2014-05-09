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




""" DAVPrecondition controller"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

# python import

# kolekti imports
from kolekti.http import statuscodes as HS
from kolekti.exceptions import exceptions as EXC
from kolekti.logger import debug,dbgexc
#from Locks.Lock import Lock
#from Locks.constants import LOCK_DEPTH_INFINITE, LOCK_SCOPE_EXCLUSIVE, LOCK_SCOPE_SHARED, LOCK_TYPE_WRITE

# parent classes
from kolekti.mvc.controllers.HTTPPreconditionController import HTTPPreconditionController

class DAVPreconditionController(HTTPPreconditionController):

    def ctrALL(self):
        super(DAVPreconditionController,self).ctrALL()
        if not self.__evaluatePreconditionlist(self.http.headers.get("If")):
            raise EXC.PreconditionFailed

    def __evaluatePreconditionlist(self, ifheader):
        if ifheader is None:
            return True

        # Parse if header
        iflist = self.__lexer(ifheader.strip())
        for ifcond in iflist:
            pu = False
            if ifcond[0] == 'URI':
                if self.model.HASLOCK:
                    lock = self.model.abstractIO.get_lock(self.http.path)
                    pu = not lock or (lock and lock['token'] == ifcond[1])
            elif ifcond[0] == "TAG":
                etag = self.model.getEtag(self.http.path)
                if etag == ifcond[1]:
                    pu = True
            elif ifcond[0] == "NOT":
                pu = not pu
            if not pu:
                return False
        return True

    def __lexer(self, ifheader, iflist=set(), curpos=0):
        if curpos >= len(ifheader)-1:
            return iflist

        while ifheader[curpos] == ' ' or ifheader[curpos] == '\n':
            curpos += 1

        curif = ifheader[curpos]
        if curif == "<":
            p = ifheader.find('>')
            uri = ifheader[curpos+1:p]
            curpos += p
            iflist.add(('URI', uri))
        elif curif == "[":
            p = ifheader.find(']')
            tag = ifheader[curpos+1:p]
            curpos += p
            iflist.add(('ETAG', tag))
        elif curif == "N":
            curpos += 3
            iflist.add(('NOT', 'not'))
        else:
            iflist.add(('CHAR', curif))
        return self.__lexer(ifheader, iflist, curpos)
