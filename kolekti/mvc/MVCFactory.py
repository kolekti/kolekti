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




""" MVC model base classes

Abstract class for an mvc object
Generic factory object, handles quests routing
"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import sys
import imp

from kolekti.kolekticonf import conf
from kolekti.logger import debug,dbgexc

import traceback

class MatchRejected (Exception):
    """Exception class used in routing algorithm"""
    pass

class MVCLoader(object):
    def _loadMVCobject_(self,name,http,*args, **kwargs):
        # Fast path: see if the module has already been imported.
        obj = http.getobject(name)
        if obj is None:
            obj = self.__load_module(name, http, *args, **kwargs)
            http.setobject(name, obj)
        return obj

    def __load_module(self, name, http, *args, **kwargs):
        try:
            module=sys.modules[name]
            return getattr(module,name)(http,*args,**kwargs)
        except KeyError:
            pass
        # If any of the following calls raises an exception,
        # there's a problem we can't handle -- let the caller handle it.

        pathes=conf.mvcpathlist
        fp, pathname, description = imp.find_module(name,pathes)

        try:
            module = imp.load_module(name, fp, pathname, description)
            return getattr(module,name)(http,*args,**kwargs)
        except:
            dbgexc()
            return None

        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()

class MVCobject(MVCLoader):
    """
    Base class for all MVC objects
    inits the http attribute of the object
    defines methods for loading other MVC objects
    """
    def __init__(self, http):
        self.http = http

    def _loadMVCobject_(self,name,*args,**kwargs):
        return super(MVCobject,self)._loadMVCobject_(name,self.http,*args,**kwargs)
    
    def _getdata(self,namespace,key):
        return self.http.getdata(namespace,key)

    def _register_route_matchers(self):
        """ registers all matchers defined in the object class
        """
        # gets a list of tuples (name,function) for all method attributes
        # of the object named '_matcher_[name]"

        matchers=[(v[9:],getattr(self,v)) for v in dir(self) if v.startswith('_matcher_')]
        for m in matchers:
            self.http.register_matcher(m)


class MVCFactory(MVCLoader):

    def _getObjects(self, objType, httpRequest):
        """ returns an iterator on all mvc objects whose are declared as type
        matching the httpRequest in route
        """
        # get the routing directory
        route=conf.get('routes')
        # yield all objects at higher level
        for obj in route[objType]:
            yield obj
        # yield all objects in subroutes that matches
        for sroute in self._getRoute(objType,httpRequest,route):
            for obj in sroute[objType]:
                yield obj

    def _getObject(self, objType, httpRequest):
        """ returns the object that 'best matches' the request using routing
        """
        # get the root object matching the http request
        res=objType.capitalize()
        route=conf.get('routes')
        # get the latest object in root route
        for obj in route[objType]:
            res=obj
        # check if an object is defined in subroutes, get the latest
        for sroute in self._getRoute(objType,httpRequest,route):
            for obj in sroute[objType]:
                res=obj
        return res

    def _getRoute(self,objType,http,parentRoute):
        """
        an iterator that returns all subroutes recursively found
        matching the request in the parent route
        Depth-first algorithm
        """
        for route in parentRoute['subroutes']:
            if self._matchRoute(http,route):
                yield route
                if route.get('break'):
                    break
                for subroute in self._getRoute(objType,http,route):
                    yield subroute

    def _matchRoute(self,http,route):
        """
        returns true if a route matches the http request
        e.g. at least all hooks in a condition are matching
        """
        for m in route['conditions']:
            try:
                # check all hooks in the condition
                for h in m:
                    http.get_matcher(h['type'])(**h['args'])
            except MatchRejected:
                continue
            except:
                # at least on hook did not match, check next condition

                return False
            # all hooks in the condition match, route is ok
            return True
        # none of the condition were satisfied, route is nok
        return False
