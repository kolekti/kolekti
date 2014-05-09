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




""" DAV controller"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

# python import
import hashlib
import urllib2

from lxml import etree as ET

# kolekti importsdest.decode('utf-8')
from kolekti.http import statuscodes as HS

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import debug,dbgexc

# parent classes
from kolekti.mvc.controllers.PropertiesController import PropertiesController

class DAVController(PropertiesController):
    _getquery = "<propfind xmlns='DAV:'><allprop/></propfind>"

    def ctrPOST(self):
        pass

    def ctrPROPFIND(self):
        self.__davheader()
        super(DAVController,self).ctrPROPFIND()

    def ctrPROPPATCH(self):
        self.__davheader()
        super(DAVController,self).ctrPROPPATCH()

    def ctrGET(self):
        self.__davheader()
        if self.model.isResource(self.http.path):
            (data,mime,etag) = self.model.getResource(self.http.path)
            mimetype=mime[0]
            if mimetype == "application/xml":
                data = ET.XML(data)
            self._setdata('http','body',data)
            self._setdata('http','mime',mimetype)
            self._setdata('http','etag',etag)
            self.view.format_resource()
            raise EXC.OK

        elif self.model.isCollection(self.http.path):
            xmlres=ET.Element("{kolekti:ctrdata}collection")
            query=ET.XML(self._getquery)
            debug(query.xpath("/D:propfind/D:allprop", namespaces={'D':'DAV:'}))
            self.pparent=ET.SubElement(xmlres,"props")
            self.response=self.pparent
            self._props(self.http.path,query)
            for f in self.model.listCollection(self.http.path):
               if self.http.path[-1]=='/':
                   childpath=self.http.path+f
               else:
                   childpath=self.http.path+'/'+f
               m = hashlib.md5()
               m.update(childpath.encode('utf-8'))
               self.pparent=ET.SubElement(xmlres,"{kolekti:ctrdata}element")
               self.pparent.set('url',childpath)
               self.pparent.set('urlid',m.hexdigest())
               self.response=self.pparent
               self._props(childpath,query)
            self.http.setdata('http','body', xmlres)
            #debug(ET.tostring(self.http.xml(),pretty_print=True))
            self.view.format_collection()
            raise EXC.OK
        else:
            raise EXC.NotFound()


    def ctrPUT(self):
        self.__davheader()
        # do the put
        self.model.put(self.http.path)


    def ctrOPTIONS(self):
        self.__davheader()
#        if self.model.HASLOCK:
#            self.http.response.setHeader("Allow", "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE, LOCK, UNLOCK")
#        else:
#        self.http.response.setHeader("Allow", "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE")
        self.http.response.content_type="httpd/unix-directory"



    def ctrMKCOL(self):
        self.__davheader()

        # We do not support any body to MKCOL request
        if self.http.body is not '' and self.http.body is not None:
            raise EXC.UnsupportedMediaType

        # check if a resource is already mapped to this uri
        if self.model.isResource(self.http.path):
            raise EXC.MethodNotAllowed

        # check if the parent collection exists
        #debug(self.http.uri.parent)
        #if not self.model.isCollection(self.http.uri.parent.id):
        #    raise EXC.Conflict

        # perform collection creation
        self.model.createCollection(self.http.path)
        self.http.response.status="201"

    def ctrLOCK(self):
        if not self.model.HASLOCK:
            raise EXC.UnsupportedMethod
        timeout = self.http.headers.get("Timeout")
        iftoken = self.http.headers.get('If')
        if iftoken is not None:
            locktoken = iftoken[1:-1]
            token, xmldata = self.model.refresh_lock(self.http.path, locktoken)
        else:
            # else create a new lock
            depth = self.http.headers.get("Depth", 0)
            token, xmldata = self.model.create_lock(self.http.path, self.http.userId, timeout, depth, self.http.body)
        data = ET.tostring(xmldata)
        self.http.response.headers.update({'Lock-Token': "<%s>"%(token,)})
        self.http.response.body=data
        self.http.response.content_type='application/xml'
        self.http.response.status=200

    def ctrUNLOCK(self):
        self.__davheader()

        if not self.model.HASLOCK:
            raise EXC.UnsupportedMethod

        try:
            token = self.http.headers["Lock-Token"]
        except:
            raise EXC.BadRequest

        self.model.release_lock(self.http.path, token)

        self.http.response.content_type='application/xml'
        self.http.response.status=204

    def ctrDELETE(self):
        self.__davheader()
        try:
            token = self.http.headers['LOCK-TOKEN'].decode('utf8')
        except:
            token=None
        self.model.delete(self.http.path)
        self.http.response.status="207"

    def ctrCOPY(self):
        self.__davheader()
        udest=self.model.url2id(self.http.headers['Destination'])
        #debug("COPY %s %s with %s" %(self.http.path, dest, self.model.copy))
        self.model.copy(self.http.path, udest)
        self.http.response.status="207"

    def ctrMOVE(self):
        self.__davheader()
        try:
            udest=self.model.url2id(self.http.headers['Destination'])
            self.model.move(self.http.path, udest)
            self.http.response.status=207
        except KeyError:
            raise EXC.BadRequest

    def __davheader(self):
        if self.model.HASLOCK:
            self.http.response.headers.update({"Allow": "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE, LOCK, UNLOCK","DAV":"1,2"})
        else:
            self.http.response.headers.update({"Allow": "OPTIONS, GET, HEAD, POST, COPY, MOVE, PUT, PROPFIND, PROPPATCH, MKCOL, DELETE","DAV":"1,2"})
