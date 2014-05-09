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


""" user info model class"""

__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import subprocess
import os

from lxml import etree as ET

from kolektiserver.kolekticonf import conf
from kolekti.logger import debug
from kolekti.exceptions import exceptions as EXC
#from kolekti.mvc.models.sql.models import Users
#from kolektiserver.models.sql.models import Projects, ProjectUser

from kolekti.mvc.models.Model import Model
from kolekti.mvc.models.PassUtils import PassUtils
from kolekti.mvc.models.Properties import Properties

class UserAccountModel(Model, PassUtils, Properties):
    __localNS={"kolekti:userinfo":"kui"}

    def create_user(self,login,password,firstname='',lastname='',email='',organization='',lang='fr',timezone='UTC',admin=False,translator=False):
        """ adds a user to the authent file
        """
        passhash = self._encode_password(password)

        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "login='%s'" %login)
        if not user == []:
            raise EXC.Error, "Login already exists"
        else:
            user = Users(login, passhash, firstname=firstname, lastname=lastname, email=email, organization=organization, lang=lang, timezone=timezone, is_active=True, is_admin=admin, is_translator=translator)
            sql.insert(user, autocommit=False)
        if conf.get('svn'):
            cmd = ['htpasswd','-b', conf.get('svn_passwdfile'), login,  password]
            if not os.path.isfile(conf.get('svn_passwdfile')):
                cmd.insert(1, '-c')
            debug("mycmd = %s" %str(cmd))
            if subprocess.call(cmd) != 0:
                sql.rollback()
                raise EXC.Error, "Failed execute cmd: %s" %cmd
        sql.commit()
        return user.id

    def get_user(self, uid):
        try:
            users = self.getUsers()
            return users.xpath("/users/user[@uid='%d']" %uid)[0]
        except:
            return None

    def update_infos_user(self,uid,password='',firstname='',lastname='',email='',organization='',lang='fr',timezone='UTC',admin=False,translator=False):
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "id='%d'" %uid)
        if not user == []:
            u = user[0]
            if password != '':
                u.password = self._encode_password(password)
            u.firstname = firstname
            u.lastname = lastname
            u.email = email
            u.organization = organization
            u.lang = lang
            u.timezone = timezone
            u.is_admin = admin
            u.is_translator = translator
        if conf.get('svn') and password != '':
            cmd = ['htpasswd','-b', conf.get('svn_passwdfile'), user[0].login,  password]
            if not os.path.isfile(conf.get('svn_passwdfile')):
                cmd.insert(1, '-c')
            debug("mycmd = %s" %str(cmd))
            if subprocess.call(cmd) != 0:
                sql.rollback()
                raise EXC.Error, "Failed execute cmd: %s" %cmd
        sql.commit()

    def update_password(self, uid, password):
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "id='%d'" %uid)
        if not user == []:
            u = user[0]
            u.password = self._encode_password(password)
        # update passwdfile for svn access
        if conf.get('svn'):
            cmd = ['htpasswd','-b', conf.get('svn_passwdfile'), user[0].login, password]
            if not os.path.isfile(conf.get('svn_passwdfile')):
                cmd.insert(1, '-c')
            debug("mycmd = %s" %str(cmd))
            if subprocess.call(cmd) != 0:
                sql.rollback()
                raiseEXC.Error, "Failed execute cmd: %s" %cmd
        sql.commit()

    def delete_user(self,uid):
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "id='%d'" %uid)
        if not user == []:
            sql.delete(user[0], autocommit=False)
        if conf.get('svn'):
            cmd = ['htpasswd','-D', conf.get('svn_passwdfile'), user[0].login]
            if subprocess.call(cmd) != 0:
                sql.rollback()
                raiseEXC.Error, "Failed execute cmd: %s" %cmd

        ProjectUser = sql.get_model('ProjectUser')
        res = sql.select(ProjectUser, "user_id='%d'" %uid)
        sql.delete(res, autocommit=False)
        sql.commit()
        self.updateSvnGroupFile()

    def getProjects(self):
        ''' Get list of projects '''
        projects = ET.Element("projects")
        sql = self.http.dbbackend
        Projects = sql.get_model('Projects')
        ProjectUser = sql.get_model('ProjectUser')
        res = sql.select(Projects)
        for p in res:
            prj = ET.SubElement(projects, "project", {'id':str(p.id), 'name': p.name, 'dir': p.directory, 'lang': p.lang})
            desc = ET.SubElement(prj, "description")
            desc.text = p.description
            users = ET.SubElement(prj, "users")
            for uprj in sql.select(ProjectUser, "project_id = %d" %p.id):
                ET.SubElement(users, "user", {'uid':str(uprj.user_id)})
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
            lang = ET.SubElement(user, "lang")
            lang.text = u.lang
            timezone = ET.SubElement(user, "timezone")
            timezone.text = u.timezone
            if u.is_admin:
                user.set('isadmin', 'yes')
            if u.is_translator:
                user.set('istranslator', 'yes')
        return users

    def get_user_id(self, username):
        '''return userid from it s name'''
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        res = sql.select(Users)
        for user in res:
            if user.login == username:
                return str(user.id)
        return "0"

    def updateSvnGroupFile(self):
        '''update svn acces group file'''
        groupfile = open(conf.get('svn_groupfile'), 'w')
        groupfile.write('[groups]\n')
        projects = self.getProjects()
        users = self.getUsers()
        for project in projects.xpath('project'):
            logins = []
            for user in project.xpath('users/user'):
                debug("user id = %s" %ET.tostring(user))
                projectuser = users.xpath("/users/user[@uid='%s']" % user.get('uid'))[0]
                logins.append(projectuser.get('login'))
            # don't want to have empty groups
            if len(project.get('dir')) > 0:
                groupfile.write("%s = %s\n" % (project.get('dir').encode('utf-8'),', '.join(login.encode('utf-8') for login in logins)))
        for project in projects.xpath('project'):
            # same there, an empty name project just blocks all other
            if len(project.get('dir')) > 0:
                groupfile.write('[%s:/]\n' % project.get('dir').encode('utf-8'))
                groupfile.write('@%s = rw\n' % project.get('dir').encode('utf-8'))
        groupfile.close()

    def _prop_kui_lastname(self,*args):
        p = self._xmlprop('lastname', 'kolekti:userinfo')
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "id='%d'" %self.http.userId)[0]
        p.text=user.lastname
        return p

    def _prop_kui_firstname(self,*args):
        p = self._xmlprop('firstname', 'kolekti:userinfo')
        sql = self.http.dbbackend
        Users = sql.get_model('Users')
        user = sql.select(Users, "id='%d'" %self.http.userId)[0]
        p.text=user.firstname
        return p
