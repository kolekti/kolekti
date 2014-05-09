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


""" userdata module

This module defines storage class and marshaling/unmarshaling procedures for user session and profile data
"""

from lxml import etree as ET
from backend import backend
from kolekti.kolekticonf import conf

LXML=0
PYTHON=1

class UserData(object):
    '''
    This class manages userdata crros-process synchro and persistance :
    Uses memcache as an accessor and stores data in the backend
    Can be stored : pickleable objects and lxml Elements
    '''

    backend=None
    http=None
    
    def __init__(self,namespace,http=None):
        """ inits the service : checks if memcache is inited with this namespace, if not, load persistant data in the memcache
            inits the persistance backend
        """

        self.namespace=namespace
        self.http=http
        self.__backend()

    def __backend(self):
        if self.backend is None:
            self.backend=backend(self.namespace, self.http)

    def getParam(self,uid,key):
        """ get a record for a user xith a given key"""
        cachekey=":".join(['kolekti','services',self.namespace,str(uid),key])
        self.__backend()
        type,value=self.backend.get(self.namespace,cachekey)
        if type==LXML:
            value=ET.XML(value)
        return value

    def delete(self,uid,key):
        """ discard a key for a user"""
        cachekey=":".join(['kolekti','services',self.namespace,str(uid),key])
        self.__backend()
        self.backend.delete(self.namespace,cachekey)

    def setParam(self, uid, key, value):
        """ set a record for a user, with a key"""
        cachekey=":".join(['kolekti','services',self.namespace,str(uid),key])
        record={}
        if isinstance(value,ET._Element) or isinstance(value,ET._Document):
            record.update({'type':LXML,'value':ET.tounicode(value)})
        else:
            record.update({'type':PYTHON,'value':value})
        self.__backend()
        self.backend.set(self.namespace,cachekey,record)
