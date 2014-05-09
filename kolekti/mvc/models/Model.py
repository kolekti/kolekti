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




""" model base class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import urllib2
import time
from datetime import datetime
from pytz import timezone

from kolekti.exceptions import exceptions as EXC
from kolekti.utils.ioabstraction import iofactory
from kolekti.kolekticonf import conf
from kolekti.logger import debug,dbgexc
from kolekti.mvc.MVCFactory import MVCobject

class Model(MVCobject):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, http):
        super(Model,self).__init__(http)
        ioFact = iofactory.IOFactory()
        self.abstractIO = ioFact.getIO(http)

        self.apppath = conf.get('appdir')
        self.serverRoot = conf.get('basedir')

    # DEPRECATED
    @property
    def resid(self):
        return self.http.path

    def __timezone(self):
        tz = self.http.getdata('user', 'timezone')
        if tz is None:
            return 'GMT'
        return tz

    @property
    def tzinfo(self):
        return timezone(self.__timezone())

    # TODO Change value return
    def _geturi(self,resid):
        return resid

    def _normalize_id(self,resid):
        return self.abstractIO.normalize_id(resid)

    def _etag(self, id):
        return self.abstractIO.etag(id)

    def getEtag(self, id):
        return self._etag(id)

    def getNotFound(self):
        self.http.response.setStatus("404", "Not Found")
        self.http.response.setBody("<h1>404 - Not Found:" + self.http.uri + "</h1>")
        self.http.response.setMime("text/html")

    def getResource(self, id):
        try:
            return (self.abstractIO.getFile(id), self.abstractIO.getContentType(id), self._etag(id))
        except:
            raise EXC.NotFound

    def listCollection(self, id):
        return self.abstractIO.getDir(id)

    def isCollection(self, id):
        return self.abstractIO.isDir(id)

    def createCollection(self, id):
        return self.abstractIO.mkDir(id)

    def isResource(self, id):
        return self.abstractIO.isFile(id)

    def exists(self,id):
#        return self.abstractIO.exists(id)
        return self.isResource(id) or self.isCollection(id)

    def createResource(self,id):
        self.abstractIO.putFile(id, '')

    def delete(self, id):
        if self.abstractIO.isDir(id):
            self.abstractIO.rmdir(id)
        elif self.abstractIO.isFile(id):
            self.abstractIO.remove(id)
        else:
            raise EXC.NotFound

    def put(self, id):
        data = self.http.body
        if data is None:
            data=""
        try:
            self.abstractIO.putFile(id, data)
        except:
            dbgexc()
            raise EXC.FailedDependency

    def putdata(self, id, data):
        try:
            self.abstractIO.putFile(id, data)
        except:
            dbgexc()
            raise EXC.FailedDependency

    def move(self, id, newid):
        try:
            self.abstractIO.move(id, newid)
        except:
            dbgexc()
            raise EXC.FailedDependency

    def copy(self, id, copyid):
        if self.abstractIO.isDir(id):
            self.abstractIO.copyDirs(id, copyid)
        elif self.abstractIO.isFile(id):
            try:
                self.abstractIO.putFile(copyid, self.abstractIO.getFile(id))
            except:
                dbgexc()
                raise EXC.FailedDependency
        else:
            raise EXC.NotFound

    def url2id(self, url):
        return unicode(urllib2.unquote(url).decode('utf-8'))

    def id2url(self, id):
        return urllib2.quote(id.encode('utf-8'))

    def url2local(self, url):
        id = urllib2.unquote(url).decode('utf-8')
        return self.abstractIO.getpath(id)

    def local2url(self, path):
        id = self.abstractIO.getid(path)
        return urllib2.quote(id.encode('utf-8'))

    def _get_time(self):
        ''' Get UTC time '''
        return time.time()
