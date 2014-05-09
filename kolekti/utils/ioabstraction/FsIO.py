# -*- coding: utf-8 -*-

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

import hashlib
import os
import os.path
import time
import mimetypes
import shutil
import sys

from lxml import etree as ET

from kolekti.kolekticonf import conf
from kolekti.logger import debug,dbgexc

__author__ = "tchechme"
__date__ = "$Apr 27, 2009 11:54:13 AM$"

LOCAL_ENCODING=sys.getfilesystemencoding()


class FsIO(object):
    def __init__(self,http):
        self._basedir = conf.get('basedir')
        self.http=http

    def _id2local(self, id):
        assert type(id) is unicode, "kolekti id is not unicode in FsIO"
        try:
            if id.startswith('http://'):
                id = id.split("http://%s" %self.http.host)[-1]
            encid=id.encode(LOCAL_ENCODING)
            loc=os.path.join(self._basedir,*encid.split('/'))
            return loc
        except:
            dbgexc()
            return None

    def _local2uripath(self, path):
        assert type(path) is str, "kolekti path is not encoded in FsIO"
        p=path[len(self._basedir):]
        p='/'.join(p.split(os.path.sep))
        p=p.decode(LOCAL_ENCODING)
        return p

    def _local2id(self, path):
        assert type(path) is str, "kolekti path is not encoded in FsIO"
        p=path[len(self._basedir):]
        p='/'.join(p.split(os.path.sep))
        p=p.decode(LOCAL_ENCODING)
        return p

    def unicode2local(self, string):
        assert type(string) is unicode, "kolekti string is not unicode in FsIO"
        return string.encode(LOCAL_ENCODING)

    def local2unicode(self, localstring):
        assert type(localstring) is str, "kolekti unicode is not string in FsIO"
        return localstring.decode(LOCAL_ENCODING)

    def normalize_id(self,id):
        assert type(id) is unicode, "kolekti id is not unicode in FsIO"
        return id

    def parse(self,id,parser=None):
        path=self._id2local(id)
        return ET.parse(path,parser)

    def exists(self, id):
        path=self._id2local(id)
        return os.path.exists(path)

    def isDir(self, id):
        path=self._id2local(id)
        return os.path.isdir(path)

    def isFile(self, id):
        path=self._id2local(id)
        return os.path.isfile(path)

    def isResource(self, id):
        path=self._id2local(id)
        return os.path.isfile(path)

    def etag(self, id):
        #debug('etag')
        path=self._id2local(id)
        if self.isDir(id):
            token="collection:"+id+":".join(self.getDir(id))
            m=hashlib.md5()
            m.update(token.encode('utf-8'))
            #debug('etag dir %s'%m.hexdigest())
            return m.hexdigest()
        else:
            #return md5.new(self.getFile(uri)).hexdigest()
            m=hashlib.md5()
            m.update(str(self.getUpdateDate(id)))
            #debug('etag file %s'%m.hexdigest())
            return m.hexdigest()

    def getpath(self, id):
        return self._id2local(id)

    def getid(self, path):
        return self._local2id(path)
    
    def isNewer(self, id1, id2):
        return self.getUpdateDate(id1) > self.getUpdateDate(id2)

    def getFile(self, id):
        path=self._id2local(id)
        s = ""
        fp = open(path, "rb")
        while 1:
            a = fp.read()
            if not a: break
            s = s + a
        fp.close()
        return s

    def getContentType(self, id):
        path=self._id2local(id)
        return mimetypes.guess_type(path)

    # def getUpdateDateSeconds(self, id, utc=0):
    #     path=self._id2local(id)
    #     #return time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(os.path.getmtime(path)))
    #     return self.__get_path_time(path)

    def getUpdateDate(self, id):
        # returns the timestap of modification time of the resource
        path=self._id2local(id)
        return os.path.getmtime(path)

    def getCreationDate(self, id):
        path=self._id2local(id)
        return os.path.getctime(path)

    def getSize(self, id):
        path=self._id2local(id)
        return os.path.getsize(path)

    def getDir(self, id):
        path=self._id2local(id)
        if self.isDir(id):
            return [e.decode(LOCAL_ENCODING) for e in os.listdir(path)]
        else:
            return []

    def getDirRec(self, id):
        path=self._id2local(id)
        w=os.walk(path, False)
        r=[]
        for dd in [d for d in w if not ".svn" in d[0].split(os.path.sep)]:
            r.append((self._local2id(dd[0]),0))
            for res in dd[2]:
                r.append((self._local2id(os.path.join(dd[0],res)),1))
        return r

    def mkDir(self, id):
        path=self._id2local(id)
        os.mkdir(path)

    def makedirs(self, id):
        if not self.isDir(id):
            path=self._id2local(id)
            dir=os.path.dirname(path)
            os.makedirs(dir)

    def remove(self, id):
        path=self._id2local(id)
        os.remove(path)

    def rmdir(self, id):
        path=self._id2local(id)
        shutil.rmtree(path)

    def walk(self, id, topdown=False):
        path=self._id2local(id)
        return os.walk(path, topdown)

    def copyFile(self, id, destid):
        path=self._id2local(id)
        destpath=self._id2local(destid)
        shutil.copyfile(path,destpath)

    def putFile(self, id, data):
        assert type(data) is str, "kolekti data is not str in FsIO"
        path=self._id2local(id)
        try:
            self.makedirs(id)
        except:
            pass
        fp = open(path, "w")
        fp.write(data)
        fp.close()

    def move(self, id, newid):
        path=self._id2local(id)
        newpath=self._id2local(newid)
        os.rename(path, newpath)

    def copyDirs(self, id, destid, ignore=shutil.ignore_patterns(".svn",)):
        path=self._id2local(id)
        destpath=self._id2local(destid)
        shutil.copytree(path, destpath, ignore=ignore)

    def __get_path_time(self, path):
        return os.path.getctime(path)
        
