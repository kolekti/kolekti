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


""" Project model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
import hashlib
import urllib2
import time

from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolekti.logger import dbgexc, debug
#from kolekti.mvc.models.sql.models import Users

from kolekti.mvc.models.BrowserModel import BrowserModel
#from kolektiserver.models.sql.models import Projects, ProjectUser, ProjectScripts

class ProjectModel(BrowserModel):
    __localNS={"kolekti":"k",
               "kolekti:scripts":"ks",
               "kolekti:trames":"kt"}

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(ProjectModel,self).__init__(*args,**kwargs)

    #def url2id(self, url):
    #    ''' Convert url to id '''
    #    id = urllib2.unquote(url).decode('utf-8')
    #    return self.abstractIO.normalize_id(id)

    def id2url(self, id):
        ''' Convert id to url '''
        id = self.abstractIO.normalize_id(id)
        return urllib2.quote(id.encode('utf-8'))

    @property
    def project(self):
        ''' Get informations of current project '''
        try:
            sql = self.http.dbbackend
            Projects = sql.get_model('Projects')
            prj = sql.select(Projects, "directory = '%s'" %self.http.path.split('/')[2])[0]
            return ET.Element('project',
                              {"id": str(prj.id),
                               "name": prj.name,
                               "directory": prj.directory,
                               "description": prj.description,
                               "lang": prj.lang})
        except:
            dbgexc()
            return None

    @property
    def lang(self):
        ''' Get lang of current project '''
        try:
            sql = self.http.dbbackend
            Projects = sql.get_model('Projects')
            res = sql.select(Projects, "directory = '%s'" %self.project.get('directory'))
            return res[0].lang
        except:
            dbgexc()
            return 'fr'

    def checkProjectAccess(self, prj):
        ''' Check if user can access at current project '''
        projects = self.getProjectsList()
        try:
            # try to get project
            projects.xpath("/projects/project[@dir='%s']" %prj)[0]
            return True
        except IndexError:
            return False
        
    def getPubscripts(self):
        ''' Get scripts configuration file '''
        return ET.parse(conf.get('pubscripts')).getroot()

    def getProjectPubscripts(self):
        ''' Get list of scripts for current project '''
        pubscripts = self.getPubscripts()
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        ProjectScripts = sql.get_model('ProjectScripts')
        prj = sql.select(Projects, "directory = '%s'" %self.project.get('directory'))[0]
        res = sql.select(ProjectScripts, "project_id = %d" %prj.id)

        pscripts = ET.Element("scripts")
        for script in res:
            try:
                pscripts.append(pubscripts.xpath("/scripts/pubscript[@id='%s']" %script.script_id)[0])
            except:
                dbgexc()
        return pscripts

    def getProjectsList(self):
        ''' Get xml to list projects '''
        data = self.__projectslist()
        prj = data.xpath("/projects/project[users/user[@uid = %d]]" %int(self.http.userId))
        projects = ET.Element("projects")
        for p in prj:
            projects.append(p)
        return projects

    def getUsers(self):
        ''' Get list of users '''
        users = ET.Element("users")
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        res = sql.select(Users)
        for u in res:
            user = ET.SubElement(users, "user", {'login': u.login, 'uid': str(u.id)})
            fname = ET.SubElement(user, "firstname")
            fname.text = u.firstname
            lname = ET.SubElement(user, "lastname")
            lname.text = u.lastname
            email = ET.SubElement(user, "email")
            email.text = u.email
            org = ET.SubElement(user, "organization")
            org.text = u.organization
            if u.is_admin:
                user.set('isadmin', 'yes')
            if u.is_translator:
                user.set('istranslator', 'yes')
        return users

    def getUsername(self, uid):
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        res = sql.select(Users, 'id = %d' %uid)
        if res == []:
            return ""
        else:
            return res[0].lastname+' '+res[0].firstname

    def _urihash(self, uri):
        ''' Hash uri '''
        m = hashlib.md5()
        m.update(uri.encode("utf8"))
        return m.hexdigest()

    _history_filter=lambda self,p:True
    
    def _history(self, resid):
        res=ET.Element('listfiles')
        try:
            histo=self.abstractIO.history(resid,filterfct=self._history_filter,limit=10)
            for item in histo:
                i=ET.SubElement(res,
                                'file',
                                resid='@'+item.get('path'),
                                uid=str(item.get('uid')),
                                author=item.get('author'),
                                revnum=str(item.get('number')),
                                time=str(item.get('date')),
                                msg=item.get('msg')
                                )
        except:
            dbgexc()
            pass
        return res
        
    def __old__get_log(self, resid):
        logdir=self._normalize_id(resid).split(u'/')[:4]
        log = u'/'.join(logdir+[u'_manifest.xml'])
        if self.abstractIO.exists(log):
            return self.abstractIO.parse(log).getroot()
        else:
            return None

    def log_save(self, resid):
        logdir=self._normalize_id(resid).split(u'/')[:4]
        log = u'/'.join(logdir+[u'_manifest.xml'])
        if self.abstractIO.exists(log):
            d = self.abstractIO.parse(log)
            root = d.getroot()
        else:
            root = ET.Element('listfiles')
        ET.SubElement(root, 'file', {'time':str(time.time()),'uid':str(self.http.userId),'resid':resid})
        self.abstractIO.putFile(log,ET.tostring(root,pretty_print=True))

    def list_orders(self):
        orders = ET.Element("orders")
        path = u'/projects/%s/configuration/orders' %self.project.get('directory')
        for l in self.listCollection(path):
            ET.SubElement(orders, "order", {"path":path, "src":l})
        return orders

    def __projectslist(self):
        ''' Get list of projects '''
        projects = ET.Element("projects")
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        ProjectUser = sql.get_model('ProjectUser')
        res = sql.select(Projects)
        for p in res:
            prj = ET.SubElement(projects, "project", {'name': p.name, 'dir': p.directory, 'lang': p.lang})
            desc = ET.SubElement(prj, "description")
            desc.text = p.description
            users = ET.SubElement(prj, "users")
            for uprj in sql.select(ProjectUser, "project_id = %d" %p.id):
                ET.SubElement(users, "user", {'uid':str(uprj.user_id)})
        return projects

    ###############################################
    # DAV Methods
    ###############################################

    # Scripts
    def _prop_ks_pubscripts(self, resid):
        ''' Define pubscripts '''
        p = self._xmlprop('pubscripts', 'kolekti:scripts')
        p.append(self.getProjectPubscripts())
        return p

    # Trames
    def _prop_kt_trames(self, resid):
        ''' Define list of trames '''
        p = self._xmlprop('trames', 'kolekti:trames')
        for f in self.listCollection(u'@trames'):
            trame = '@trames/%s' %f
            if self.isResource(trame):
                t = ET.SubElement(p, "trame", {'src': trame})
                t.text = self._prop_dav_displayname(trame).text.split('.xml')[0]
        return p

    def _prop_k_resid(self, resid):
        ''' Get resid of resource '''
        p = self._xmlprop('resid','kolekti')
        #p.text = uri.objname
        id = self.http.getdata('kolekti','resid')
        if not id:
            id = resid
        p.text = id
        return p

    def _prop_k_history(self, resid):
        """history of a resource or collection"""
        p = self._xmlprop('history','kolekti')
        p.append(self._history(resid))
        return p

    def _prop_k_revision(self, resid):
        """last revision of current project"""
        p = self._xmlprop('revision','kolekti')
        try:
            p.text = str(self.abstractIO.svnlog(u'@', 1)[0].get('number'))
        except:
            p.text = ""
        return p
