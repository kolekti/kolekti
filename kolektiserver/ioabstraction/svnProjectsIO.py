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


import subprocess
import os
import urllib2
import pysvn
import shutil
import stat

from kolektiserver.kolekticonf import conf
from kolektiserver.ioabstraction.FsProjectsIO import FsProjectsIO

from kolekti.utils.ioabstraction.FsIO import LOCAL_ENCODING
from kolekti.utils.ioabstraction.svnIO import svnIO
from kolekti.logger import debug, dbgexc
from kolekti.utils.i18n.i18n import tr

class svnProjectsIO(svnIO,FsProjectsIO):
    def __init__(self,http):
        FsProjectsIO.__init__(self,http)
        svnIO.__init__(self,http)


    def initProject(self,project):
        debug("init in svn")
        projectpath=self._id2local(u'/projects/%s'%project)
        if os.path.exists(projectpath):
            debug("project path %s already exists"%projectpath)
            raise Exception

        repospath=self._id2local(u'/repositories')

        if not os.path.isdir(repospath):
            os.mkdir(repospath)

        if conf.get('svn'):
            # use svnadmin command to create repository
            projectrepospath=self._id2local(u'/repositories/%s'%project)
            cmd=["svnadmin","create","%s"%projectrepospath]
            if subprocess.call(cmd)!=0:
                raise Exception

            # add hooks to svn if svn external access enabled

            # start-commit hook
            shutil.copyfile(os.path.join(conf.get('confdir').encode(LOCAL_ENCODING),'start-commit'),
                            os.path.join(projectrepospath, 'hooks', 'start-commit'))
            os.chmod(os.path.join(projectrepospath, 'hooks', 'start-commit'),
                     stat.S_IXUSR | stat.S_IRUSR)

            # post-commit hook
            post_commit_hook = open(os.path.join(projectrepospath, 'hooks', 'post-commit'), 'w')
            post_commit_template = open(os.path.join(conf.get('confdir').encode(LOCAL_ENCODING),'post-commit'), 'r')
            for line in post_commit_template:
                post_commit_hook.write(line.replace('@project_basedir@', conf.get('basedir')))
            post_commit_hook.close()
            post_commit_template.close()
            os.chmod(os.path.join(projectrepospath, 'hooks', 'post-commit'),
                     stat.S_IXUSR | stat.S_IRUSR)

        # import _base_template into repository
        tplpath = self._id2local(u'/_base_template')
        projectreposurl='file://'+urllib2.quote(projectrepospath)
        s = tr(u"[0030]Initialisation du projet Kolekti")
        rev=self._client.import_(tplpath,projectreposurl,s.i18n(self.http.translation))
        # checkout the repository
        self._client.checkout(projectreposurl,projectpath)

    def _update_repo(self):
        project=self.http.getdata('kolekti', 'project')
        self.updateProject(project.get('directory',''))

    def updateProject(self, project):
        ''' Update svn project '''
        try:
            projectpath=self._id2local_unicode(u'/projects/%s'%project)
            self._client.update(projectpath)
        except:
            dbgexc()

    def removeProject(self, project):
        ''' Remove svn project '''
        shutil.rmtree(self._id2local(u'/projects/%s'%project))
        shutil.rmtree(self._id2local(u'/repositories/%s'%project))
