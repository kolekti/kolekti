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




""" model : Properties class"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

from lxml import etree as ET
from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc,debug


class Properties(object):
    def __init__(self,http,ns={}):
        try:
            self.PNS.update(ns)
        except AttributeError:
            self.PNS=ns
        self.RPNS = dict((value, key) for key, value in self.PNS.iteritems())

    def getproplist(self, resid):
        props = [tuple(v[6:].split('_', 1)) for v in dir(self) if v.startswith('_prop_')]
        try:
            props = [(self.RPNS[ns], p) for (ns, p) in props]
        except KeyError:
            dbgexc()
            return []
        return props

    def getpropval(self, resid, propname, ns):
        pname=propname.replace("-", "")
        try:
            self.PNS[ns]
        except KeyError:
            raise EXC.NotFound, ('no such property namespace %s'%ns,)
        mname = "_prop_%s_%s"%(self.PNS[ns],pname)
        try:
            method = getattr(self, mname)
        except AttributeError:
            raise EXC.NotFound, ('no such property %s:%s'%(ns,propname),)
        try:
            r = method(resid)
        except EXC.Error as e:
            raise e
        except:
            dbgexc()
            raise EXC.AppError, ('Unknown error getting property %s:%s',(ns,propname),)
        return r

    def proppatch_prepare(self, resid):
        pass

    def proppatch_begin(self, resid):
        pass

    def proppatch_commit(self):
        pass

    def proppatch_rollback(self):
        pass

    def setpropval(self, resid, propname, ns, value):
        pname=propname.replace("-", "")
        try:
            self.PNS[ns]
        except KeyError:
            raise EXC.NotFound, ('no such property',)
        mname = "_setprop_%s_%s"%(self.PNS[ns],pname)
        try:
            method = getattr(self, mname)
        except AttributeError:
            raise EXC.NotFound, ('no such property',)
        return method(resid, value)

    def addpropval(self, resid, propname, ns, value):
        pname=propname.replace("-", "")
        try:
            self.PNS[ns]
        except KeyError:
            raise EXC.NotFound, ('no such property',)
        mname = "_addprop_%s_%s"%(self.PNS[ns],pname)
        try:
            method = getattr(self, mname)
        except AttributeError:
            raise EXC.NotFound, ('no such property',)
        return method(resid, value)

    def delprop(self, resid, propname, ns):
        pname=propname.replace("-", "")
        try:
            self.PNS[ns]
        except KeyError:
            raise EXC.NotFound, ('no such property',)
        mname = "_delprop_%s_%s"%(self.PNS[ns],pname)
        try:
            method = getattr(self, mname)
        except AttributeError:
            raise EXC.NotFound, ('no such property',)
        return method(resid)

    def _xmlprop(self, name, ns):
        return ET.Element("{" + ns + "}" + name)
