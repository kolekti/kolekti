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


"""
    Administration model
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os

from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolekti.logger import dbgexc,debug
#from kolekti.mvc.models.sql.models import Users

from kolektiserver.models.UserAccountModel import UserAccountModel
#from kolektiserver.models.sql.models import Projects, ProjectUser, ProjectScripts, Criterias, CriteriaValues, Usecase

class AdminModel(UserAccountModel):

    @property
    def project(self):
        ''' Get informations of current project '''
        projectmodel = self._loadMVCobject_('ProjectModel')
        return projectmodel.project

    @property
    def isadmin(self):
        return True

    def getPubscripts(self):
        ''' Get list of scripts '''
        return ET.parse(os.path.join(conf.get('appdir'),conf.get('pubscripts'))).getroot()

    def attach_userprojects(self, uid, projects):
        sql = self.http.dbbackend
        ProjectUser = sql.get_model('ProjectUser')
        Projects = sql.get_model('Projects')
        # remove existing projects for user
        prj = sql.select(ProjectUser, "user_id = '%s'" %uid)
        sql.delete(prj)
        # insert new record of project access
        uprj = []
        for project in projects:
            prj = sql.select(Projects, "directory = '%s'" %project)[0]
            uprj.append(ProjectUser(prj.id, uid))
        sql.insert(uprj)
        if conf.get('svn'):
            self.updateSvnGroupFile()

    def archiveProject(self, pid):
        ''' Create zip file for a current project '''
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        prj = sql.select(Projects, "id = %d" %pid)[0]
        zipname = "%s.zip" %prj.directory
        zip = self._loadMVCobject_('ZipFileIO')
        zip.open(self.abstractIO.getpath(u"/projects/%s"%zipname), 'w')
        try:
            self.__set_archive_files(zip, u'/projects/%s' %prj.directory)
            self.__set_archive_db(sql, zip, prj)
        except:
            dbgexc()
            zipname = ''
        zip.close()
        return zipname

    def getArchiveProject(self, pid):
        ''' Get name of zip file for a current project '''
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        prj = sql.select(Projects, "id = %d" %pid)[0]
        zipname = "%s.zip" %prj.directory
        if self.abstractIO.exists(u"/projects/%s"%zipname):
            return zipname
        return ''

    def getProject(self, pid):
        try:
            sql = self.http.dbbackend
            Projects = sql.get_model('Projects')
            prj = sql.select(Projects, "id = %d" %pid)[0]
            return ET.Element('project',
                              {"id": str(prj.id),
                               "name": prj.name,
                               "directory": prj.directory,
                               "description": prj.description,
                               "lang": prj.lang})
        except:
            return None

    def deleteProjects(self, projects):
        ''' Delete projects dir '''
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        ProjectUser = sql.get_model('ProjectUser')
        ProjectScripts = sql.get_model('ProjectScripts')
        Criterias = sql.get_model('Criterias')
        CriteriaValues = sql.get_model('CriteriaValues')
        Usecase = sql.get_model('Usecase')
        res = []
        for pid in projects:
            try:
                pid = int(pid)
                prj = sql.select(Projects, "id = %d" %pid)[0]
                #remove project from svn
                self.abstractIO.removeProject(prj.directory)

                # remove project entries in DB
                res.append(prj)
                res.extend(sql.select(ProjectUser, "project_id = %d" %pid))
                res.extend(sql.select(ProjectScripts, "project_id = %d" %pid))

                # remove criterias entries
                criterias = sql.select(Criterias, "pid = %d" %pid)
                res.extend(criterias)
                for crit in criterias:
                    res.extend(sql.select(CriteriaValues, "criteria_id = %d" %crit.id))

                # remove usecases entries
                usecases = sql.select(Usecase, "project_id=%d" %pid)
                res.extend(usecases)

                #remove projet from svn groupfile
                self.updateSvnGroupFile()
            except:
                dbgexc()
        sql.delete(res)
        sql.close()

    def newProject(self, name, dir, desc, lang):
        ''' Create new project '''
        try:
            sql = self.http.dbbackend
            Projects = sql.get_model('Projects')
            prj = Projects(name,dir,desc,lang)
            sql.insert(prj, autocommit=False)
            #Create directory
            self.abstractIO.initProject(dir)
            sql.commit()
            return prj.id
        except:
            sql.rollback()
            return 0

    def updateProject(self, pid, name, desc, lang):
        ''' Update one project '''
        try:
            sql = self.http.dbbackend
            Projects = sql.get_model('Projects')
            prj = sql.select(Projects, "id = %d" %pid)[0]
            prj.name = name
            prj.description = desc
            prj.lang = lang
            sql.commit()
            return prj.id
        except:
            sql.rollback()
            return 0

    def removeUserProject(self, uid, pid):
        ''' Remove one user of project '''
        sql = self.http.dbbackend
        ProjectUser = sql.get_model('ProjectUser')
        uprj = sql.select(ProjectUser, "project_id = %d and user_id = %d" %(pid, uid))[0]
        try:
            sql.delete(uprj)
        except:
            sql.rollback()
            raise
        if conf.get('svn'):
            self.updateSvnGroupFile()

    def addUserProject(self, uid, pid):
        ''' Add one user of project '''
        sql = self.http.dbbackend
        ProjectUser = sql.get_model('ProjectUser')
        uprj = ProjectUser(pid, uid)
        try:
            sql.insert(uprj)
        except:
            sql.rollback()
            raise
        if conf.get('svn'):
            self.updateSvnGroupFile()

    def getUserProjects(self, uid):
        ''' Get all projects for user '''
        data = self.getProjects()
        return data.xpath("/projects/project[users/user/@uid = %d]" %uid)

    def getProjectScripts(self, pid):
        ''' Get list of pubqscripts '''
        scripts = ET.Element("scripts")
        sql = self.http.dbbackend
        ProjectScripts = sql.get_model('ProjectScripts')
        res = sql.select(ProjectScripts, "project_id=%d" %pid)
        for script in res:
            ET.SubElement(scripts, "pubscript", {'id': script.script_id})
        return scripts

    def setScriptsProject(self, pid, scripts):
        ''' Set scripts of a project'''
        prjscripts = []
        sql = self.http.dbbackend
        ProjectScripts = sql.get_model('ProjectScripts')
        for s in scripts:
            prjscripts.append(ProjectScripts(pid, s))
        # Remove all existing scripts
        res = sql.select(ProjectScripts, "project_id = %d" %pid)
        sql.delete(res)
        # Try to insert new scripts
        try:
            sql.insert(prjscripts)
        except:
            sql.rollback()
            raise

    def genUsecases(self, pid):
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        Usecase = sql.get_model('Usecase')
        prj = sql.select(Projects, "id = %d" %pid)[0]
        # reset usecase
        res = sql.select(Usecase, "project_id = %d" %pid)
        sql.delete(res)
        try:
            self.__modules_usecases(sql, pid, u'@modules', prj.directory)
            self.__trame_usecases(sql, pid, u'@trames', prj.directory)
            self.__orders_usecases(sql, pid, u'@configuration/orders', prj.directory)
            sql.commit()
            return True
        except:
            dbgexc()
            sql.rollback()
            return False

    def normalize_id(self, resid, prj):
        if resid[0] == "@":
            return u'/projects/%s/%s' %(prj, resid[1:])
        return resid

    def __trame_usecases(self, sql, pid, trameurl, prj):
        ''' Set trame usecases '''
        Usecase = sql.get_model('Usecase')
        for (path, type) in self.abstractIO.getDirRec(self.normalize_id(trameurl, prj)):
            if type == 1:
                try:
                    xtrame = ET.XML(self.abstractIO.getFile(path))
                    for mod in xtrame.xpath('//kt:module', namespaces={"kt": "kolekti:trames"}):
                        modpath = self.normalize_id(mod.get('resid'), prj)
                        if modpath.startswith('/projects/%s' %prj):
                            sql.insert(Usecase(pid, path, modpath, 0), autocommit=False)
                except ET.XMLSyntaxError:
                    debug('Failed to parse file: %s' %path)

    def __modules_usecases(self, sql, pid, modurl, prj):
        ''' Set modules usecases '''
        Usecase = sql.get_model('Usecase')
        for (path, type) in self.abstractIO.getDirRec(self.normalize_id(modurl, prj)):
            if type==1:
                try:
                    xmodurl = ET.XML(self.abstractIO.getFile(path))
                    for img in xmodurl.xpath('//h:img|//h:embed', namespaces={"h": "http://www.w3.org/1999/xhtml"}):
                        imgpath = self.normalize_id(img.get('src'), prj)
                        if imgpath.startswith('/projects/%s' %prj):
                            sql.insert(Usecase(pid, path, imgpath, 0), autocommit=False)
                except ET.XMLSyntaxError:
                    debug('Failed to parse file: %s' %path)

    def __orders_usecases(self, sql, pid, ourl, prj):
        ''' Set modules usecases '''
        Usecase = sql.get_model('Usecase')
        for (path, type) in self.abstractIO.getDirRec(self.normalize_id(ourl, prj)):
            if type == 1:
                try:
                    xourl = ET.XML(self.abstractIO.getFile(path))
                    trame = xourl.xpath("/order/trame")[0]
                    trpath = self.normalize_id(trame.get('value', ''), prj)
                    if trpath.startswith('/projects/%s' %prj):
                        sql.insert(Usecase(pid, path, trpath, 0), autocommit=False)
                except (ET.XMLSyntaxError, IndexError):
                    debug('Failed to parse file: %s' %path)

    def __set_archive_files(self, zip, id):
        FsIO=self._loadMVCobject_('FsIO')
        for (curid, type) in FsIO.getDirRec(id):
            if type == 1:
                zippath = '/'.join(curid.split('/')[3:])
                zip.write(self.abstractIO.getpath(curid), zippath)

    def __set_archive_db(self, sql, zip, prj):
        Criterias = sql.get_model('Criterias')
        CriteriaValues = sql.get_model('CriteriaValues')
        MasterFilter = sql.get_model('MasterFilter')

        buf = "Projects|%d|%s|%s|%s|%s\n" %(prj.id, prj.name, prj.directory, prj.description, prj.lang)
        rescrit = sql.select(Criterias, "pid = %d" %prj.id)
        for crit in rescrit:
            rescritval = sql.select(CriteriaValues, "criteria_id = %d" %crit.id)
            buf += "Criterias|%d|%d|%s|%s|%s\n" %(crit.id, crit.pid, crit.name, crit.code, crit.type)
            for critval in rescritval:
                buf += "CriteriaValues|%d|%d|%s|%s\n" %(critval.id, critval.criteria_id, critval.value1, critval.value2)

        mfilters = sql.select(MasterFilter, "pid = %d" %prj.id)
        for mf in mfilters:
            buf += "MasterFilter|%d|%d|%s\n" %(mf.id, mf.pid, mf.value)

        zip.writestr(u"projectdb.data", buf.encode('utf-8'))
