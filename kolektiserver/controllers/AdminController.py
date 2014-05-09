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


"""controller for administration"""

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc, debug

from kolektiserver.controllers.WWWController import WWWController

class AdminController(WWWController):
    state = True

    def ctrGET(self):
        ''' Check if user can access '''
        if not self.http.admin:
            raise EXC.Forbidden

        self._setdata('kolekti', 'projects', self.model.getProjects())
        self._setdata('kolekti', 'users', self.model.getUsers())
        if self.http.path.startswith('/admin/projects/scripts'):
            pid = int(self.http.path.split('/')[-1])
            self._setdata('kolekti', 'scripts', self.model.getPubscripts())
            self._setdata('kolekti', 'projectscripts', self.model.getProjectScripts(pid))
        elif self.http.path.startswith('/admin/projects/maintenance'):
            pid = int(self.http.path.split('/')[-1])
            zipname = self.model.getArchiveProject(pid)
            if zipname != '':
                self._setdata('project', 'archive', zipname)
                if self.http.path.startswith('/admin/projects/maintenance/archive'):
                    self._setdata('http', 'body', self.model.abstractIO.getFile(u'/projects/%s' %zipname))
                    self.http.response.content_disposition = 'attachment; filename="%s"' %zipname.encode('utf-8')
                    self.view.format_resource()
                    return

        self.view.format_collection()

    def ctrPOST(self):
        # PROJECTS
        if not self.http.admin:
            raise EXC.Forbidden
        else:
            if self.http.path == '/admin/projects':
                self.__actionsProjects()
            elif self.http.path.startswith('/admin/projects/users'):
                self.__usersProject()
            elif self.http.path.startswith('/admin/projects/params'):
                self.__editProject()
            elif self.http.path.startswith('/admin/projects/scripts'):
                self.__setScriptsProject()
            elif self.http.path.startswith('/admin/projects/maintenance'):
                self.__maintenance_actions()
            # USERS
            # Delete users
            elif self.http.path == '/admin/users':
                if self._get_firstparam('action') == 'delete':
                    for uid in self._get_params('deluser'):
                        self.model.delete_user(int(uid))
            # Create or update user
            elif self.http.path.startswith('/admin/users/params'):
                self.__userAccount()

            if self.state and not self._getdata('status', 'ok'):
                self._setdata('status', "ok", '')
            self.ctrGET()

    def __actionsProjects(self):
        ''' Delete or archive projects '''
        try:
            action = self._get_firstparam('action')
            if action == 'archive':
                for pid in self._get_params('project'):
                    self.model.archiveProject(int(pid))
            elif action == 'delete':
                self.model.deleteProjects(self._get_params('project'))
        except:
            self._setdata('status', "error", self._setmessage(u"[0344]Echec de lors de l'action."))
            self.state = False

    def __usersProject(self):
        ''' Remove or add user of a project '''
        pid = int(self.http.path.split('/')[-1])
        for param in self.http.params:
            if param.startswith('rem'):
                uid = int(param[3:])
                self.model.removeUserProject(uid, pid)
            elif param.startswith('add'):
                uid = int(self._get_firstparam('useradd'))
                self.model.addUserProject(uid, pid)

    def __editProject(self):
        ''' Create or update project '''
        pid = int(self._get_firstparam('id'))
        name = self._get_firstparam('name')
        dir = self._get_firstparam('dir')
        desc = self._get_firstparam('desc')
        lang = self._get_firstparam('lang')
        if pid == 0:
            id = self.model.newProject(name, dir, desc, lang)
            if id == 0:
                self._setdata('status', "error", self._setmessage(u"[0004]Echec de la création du projet."))
                self.state = False
        else:
            id = self.model.updateProject(pid, name, desc, lang)
            if id == 0:
                self._setdata('status', "error", self._setmessage(u"[0005]Echec de la mise à jour du projet."))
                self.state = False

    def __setScriptsProject(self):
        ''' Set scripts of a project'''
        pid = int(self.http.path.split('/')[-1])
        scripts = self._get_params('script')
        self.model.setScriptsProject(pid, scripts)

    def __maintenance_actions(self):
        ''' Apply maintenance action for current project '''
        pid = int(self.http.path.split('/')[-1])
        self.http.setdata('kolekti','project',self.model.getProject(pid))
        # generate archive
        if self._get_params('archive'):
            zipname = self.model.archiveProject(pid)
            if zipname == '':
                self._setdata('status', "error", self._setmessage(u"[0006]Erreur lors de la création de l'archive."))
                self.state = False
            else:
                self._setdata('status', "ok", self._setmessage(u"[0007]Création de l'archive réussie."))
                self._setdata('project', 'archive', zipname)
        # generate usecase
        if self._get_params('usecase'):
            if self.model.genUsecases(pid):
                self._setdata('status', "ok", self._setmessage(u"[0008]Régénération des cas d'usage réussi."))
            else:
                self._setdata('status', "error", self._setmessage(u"[0009]Erreur lors de la régénération des cas d'usage."))
                self.state = False

    def __userAccount(self):
        ''' Create or update an account '''
        try:
            uid = int(self.http.path.split('/')[-1])
            firstname = self._get_firstparam('firstname')
            lastname = self._get_firstparam('lastname')
            email = self._get_firstparam('email')
            org = self._get_firstparam('organization')
            locale = self._get_firstparam('locale')
            timezone = self._get_firstparam('timezone')
            login = self._get_firstparam('login')
            passwd = self._get_firstparam('pass')
            confpasswd = self._get_firstparam('pass2')
            access = self._get_firstparam('isadmin') != ''
            translator = self._get_firstparam('istranslator') != ''
            projects = self._get_params('project')

            if passwd and passwd != confpasswd:
                self._setdata('status', "error", self._setmessage(u"[0002]Les mots de passe ne correspondent pas"))
                self.state = False
            else:
                try:
                    if uid == 0 and passwd:
                        uid = self.model.create_user(login, passwd, firstname, lastname, email, org, locale, timezone, access, translator)
                        if uid == 0:
                            raise Exception, "Failed create user"
                        self.model.attach_userprojects(uid, projects)
                    elif uid != 0:
                        # update user
                        self.model.update_infos_user(uid, passwd, firstname, lastname, email, org, locale, timezone, access, translator)
                        self.model.attach_userprojects(uid, projects)
                except:
                    dbgexc()
                    self._setdata('status', "error", self._setmessage(u"[0010]Echec lors de la création de l'utilisateur"))
                    self.state = False
        except EXC.Error:
            self._setdata('status', "error", self._setmessage(u"[0011]Login déjà utilisé"))
            self.state = False

    def _get_params(self, key):
        try:
            return self.http.params.getall(key)
        except KeyError:
            return ''

    def _get_firstparam(self, key):
        try:
            return self.http.params.getone(key)
        except KeyError:
            return ''
