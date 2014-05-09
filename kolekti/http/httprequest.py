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




""" Main classes for http data management
"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import hashlib
import lxml.etree as ET
import cgi
import gettext

from kolekti.mvc.viewfactory import ViewFactory as VF
from kolekti.mvc.modelfactory import ModelFactory as MF
from kolekti.mvc.MVCFactory import MatchRejected
from kolekti.kolekticonf import conf

from webob import Request,Response

class FakeRequest(object):
    modelFact  = MF()
    viewFact  = VF()

    def __init__(self, method,path):
        self.method=method
        self.path=path
        self.__matchers={}
        self._private_data={}
        self._private_obj={}
        self.params={}
        self.headers={}
        self._sql=None

    @property
    def userId(self):
        uid=self.getdata('auth','uid')
        if uid is None:
            return 0
        return uid

    @property
    def dbbackend(self):
        if self._sql is None:
            from kolekti.utils.backends.sqlalchemybackend import SQLAlchemyBackend
            self._sql = SQLAlchemyBackend()
        self._sql.connect()
        return self._sql

    @property
    def model(self):
        return self.modelFact.getModel(self)

    @property
    def view(self):
        return self.viewFact.getView(self)

    @property
    def translation(self):
        lang=self.getdata('user','lang')
        if lang is None:
            lang = conf.get('locale_default')
        return gettext.translation(conf.get('locale_domain'),conf.get('localedir'),languages=[lang])

    def setdata(self, namespace, key, value):
        if not self._private_data.has_key(namespace):
            self._private_data.update({namespace:{}})
        self._private_data.get(namespace).update({key:value})

    def getdata(self, namespace, key):
        if not self._private_data.has_key(namespace):
            return None
        return self._private_data.get(namespace).get(key,None)

    def setobject(self, key, obj):
        if not self._private_obj.has_key(key):
            self._private_obj.update({key: obj})

    def getobject(self, key):
        return self._private_obj.get(key, None)

        # register matcher for routing
    def register_matcher(self,matcher):
        """
        registers a matcher into the request
        param matcher is a tuple (name, fct)
        """
        type=matcher[0]
        self.__matchers[type]=matcher[1]

    def get_matcher(self,name):
        """
        return a function that can perform the matching of the request
        using the matcher registered with name
        """
        fct=self.__matchers.get(name,self.null_matcher)
        return lambda **kargs : fct(self,**kargs)

    def null_matcher(self,*args,**kargs):
        """
        this matcher never matches
        used as a fallback if no matcher were registred under a name
        """
        raise MatchRejected


class WebObRequest(Request):
    viewFact  = VF()
    modelFact  = MF()
    #default_charset='utf-8'

    def __init__(self, *args, **kargs):
        kargs.update({'charset': 'utf-8'})
        super(Request,self).__init__(*args, **kargs)
        #self._uid=0
        #self._isadmin=False
        environ=kargs.get('environ',None)
        self.response=Response(environ=environ)
        self._private_data={}
        self._private_obj={}
        self._ctrs=[]
        self._sql=None
        self.__matchers={}
        #if self.headers.has_key('if'):
        #    self.If=ifHeaderManager(self.headers['if'],self.upath_info)

    @property
    def dbbackend(self):
        if self._sql is None:
            from kolekti.utils.backends.sqlalchemybackend import SQLAlchemyBackend
            self._sql = SQLAlchemyBackend()
        self._sql.connect()
        return self._sql

    # Shortcuts to frequently accesed controller data
    @property
    def userId(self):
        uid=self.getdata('auth','uid')
        if uid is None:
            return 0
        return uid

    @property
    def admin(self):
        clearances = self.getdata('auth','clearances') 
        if clearances is None:
            return False
        return "admin" in self.getdata('auth','clearances')

    @property
    def translator(self):
        clearances = self.getdata('auth','clearances') 
        if clearances is None:
            return False
        return "translator" in self.getdata('auth','clearances')

    @property
    def translation(self):
        locale=self.getdata('user','locale')
        if locale is None:
            locale = conf.get('locale_default')
        return gettext.translation(conf.get('locale_domain'),conf.get('localedir'),languages=[locale])

    @property
    def sessionId(self):
        return self.getdata('session','sid')

    @property
    def port(self):
        return self.environ.get('SERVER_PORT',80)

    @property
    def server(self):
        return self.environ.get('SERVER_NAME','127.0.0.1')

    @property
    def urlhash(self):
        m = hashlib.md5()
        m.update(self.path_info)
        return m.hexdigest()

    @property
    def path(self):
        return self.upath_info

#     def setmodel(self,model):
#         self._model=model

    @property
    def model(self):
        return self.modelFact.getModel(self)

#     def setview(self,view):
#         self._view=view

    @property
    def view(self):
        return self.viewFact.getView(self)

    def ctrmark(self, ctr):
        if not ctr in self._ctrs:
            self._ctrs.append(ctr)

    def setdata(self, namespace, key, value):
        if not self._private_data.has_key(namespace):
            self._private_data.update({namespace:{}})
        self._private_data.get(namespace).update({key:value})

    def getdata(self, namespace, key):
        if not self._private_data.has_key(namespace):
            return None
        return self._private_data.get(namespace).get(key,None)

    def setobject(self, key, obj):
        if not self._private_obj.has_key(key):
            self._private_obj.update({key: obj})

    def getobject(self, key):
        return self._private_obj.get(key, None)
    #
    #   Routing matcher functions
    #   Registers matchers from instanciated objects (controllers) into the request
    #   Performs match using all registered matchers
    #

    # register matcher for routing
    def register_matcher(self,matcher):
        """
        registers a matcher into the request
        param matcher is a tuple (name, fct)
        """
        type=matcher[0]
        self.__matchers[type]=matcher[1]

    def get_matcher(self,name):
        """
        return a function that can perform the matching of the request
        using the matcher registered with name
        """
        fct=self.__matchers.get(name,self.null_matcher)
        return lambda **kargs : fct(self,**kargs)

    def null_matcher(self,*args,**kargs):
        """
        this matcher never matches
        used as a fallback if no matcher were registred under a name
        """
        raise MatchRejected

    @property
    def xml(self):
        v=ET.Element('{kolekti:ctrdata}view')
        xml=ET.ElementTree(v)
        p={
#           'resid':self.resid,
           'uid':str(self.userId),
           'sid':str(self.sessionId),

           'method':self.method,
           'url':self.url,
#           'reluri':self.uri.relquote(),
           'uri_hash':self.urlhash,
           'host':self.host,
           'server':self.server,
           'port':self.port,
           'path':self.path,
#           'project':self.uri.project
}
        h=ET.SubElement(v,'{kolekti:ctrdata}http',p)
        e=ET.SubElement(h,'{kolekti:ctrdata}headers')
        for (hn,hv) in self.headers.items():
            ET.SubElement(e,'{kolekti:ctrdata}header',{'name':hn,'content':hv})
        if self.params is not None:
            e=ET.SubElement(h,'{kolekti:ctrdata}params')
            for (pn,plv) in self.params.items():
                if plv.__class__ == cgi.FieldStorage:
                    ET.SubElement(e,'{kolekti:ctrdata}param',{'name':pn,'type': 'file', 'content':plv.filename})
                else:
                    ET.SubElement(e,'{kolekti:ctrdata}param',{'name':pn,'content':plv})

        d=ET.SubElement(v,'{kolekti:ctrdata}data')
        for ns,data in self._private_data.iteritems():
            xns=ET.SubElement(d,'{kolekti:ctrdata}namespace')
            xns.set('id',str(ns))
            for key,value in data.iteritems():
                n=ET.SubElement(xns,'{kolekti:ctrdata}value')
                n.set('key',key)
                if ET.iselement(value):
                    n.append(value)
                else:
                    try:
                        n.text=unicode(value)
                    except:
                        #TODO : accept XML marsgalling of python objects
                        pass

        return xml
