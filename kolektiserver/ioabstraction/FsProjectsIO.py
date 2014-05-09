# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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
import urllib2

__author__ = "tchechme"
__date__ = "$Apr 27, 2009 11:54:13 AM$"



from kolekti.utils.ioabstraction.FsIO import FsIO, LOCAL_ENCODING
from kolektiserver.kolekticonf import conf
from kolekti.logger import debug


class FsProjectsIO(FsIO):
    def __init__(self,http):
        super(FsProjectsIO, self).__init__(http)

        #self.projectpart=self.uriprojectpart=''
        #project=http.getdata('kolekti', 'project')
        #print "FsProject IO, project is",project
        #if project is not None:
        #    self.projectpart=os.path.join('projects',project.get('directory'))
        #    self.uriprojectpart='/projects/%s'%project.get('directory')

    @property
    def projectpart(self):
        project=self.http.getdata('kolekti', 'project')
        if project is not None:
            return os.path.join('projects',project.get('directory').encode(LOCAL_ENCODING))
        else:
            return None

    @property
    def uprojectpart(self):
        project=self.http.getdata('kolekti', 'project')
        if project is not None:
            return os.path.join('projects',project.get('directory'))
        else:
            return None

    @property
    def uriprojectpart(self):
        project=self.http.getdata('kolekti', 'project')
        if project is not None:
            return urllib2.quote('/projects/%s'%project.get('directory').encode('UTF-8'))
        else:
            return None

    def normalize_id(self,id):
        assert type(id) is unicode, "kolekti id is not unicode in FsProjectIO"
        if id[0] == '@':
            project=self.http.getdata('kolekti', 'project')
            return u'/projects/%s/%s'%(project.get('directory'), id.strip('@'))
        else:
            return id

    def _id2local(self, id):
        assert type(id) is unicode, "kolekti id is not unicode in FsProjectIO"
        return super(FsProjectsIO,self)._id2local(self.normalize_id(id))

    def _local2id(self, path):
        assert type(path) is str, "kolekti path is not encoded in FsProjectIO"
        project=self.http.getdata('kolekti', 'project')
        lpath=os.path.join(self._basedir,
                           'projects',
                           project.get('directory').encode(LOCAL_ENCODING)
                           )
        if path[len(lpath):]==lpath:
            p=path[len(lpath):]
            p='@'+'/'.join(p.split(os.path.sep))[1:]
        else:
            p=path[len(self._basedir):]
            p='/'.join(p.split(os.path.sep))
        return p.decode(LOCAL_ENCODING)


    def etag(self, id):
        if id.split('/')[-1] == '_':
            path=self._id2local(id)
            m=hashlib.md5()
            m.update(path)
            return m.hexdigest()
        else:
            return super(FsProjectsIO, self).etag(id)


    def initProject(self,project):
        debug("init in fs")
        if self.isDir('projects/%s'%project):
            debug("already exists")
            raise
        self.copyDirs('_base_template', 'projects/%s'%project)

