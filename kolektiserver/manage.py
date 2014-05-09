#!/usr/bin/env python
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


import os
import sys
import mimetypes
import locale
import zipfile
import pysvn

LOCAL_ENCODING = sys.getfilesystemencoding()

from optparse import OptionParser, OptionGroup

os.environ['KOLEKTI_APPDIR'] = os.path.dirname(os.path.abspath(os.path.join(os.environ.get('PWD'), __file__)))
os.environ['KOLEKTI_APP'] = 'kolektiserver'

mimetypes.init()

from kolektiserver.kolekticonf import conf
from kolekti.utils.backends.sqlalchemybackend import SQLAlchemyBackend

from kolekti.mvc.MVCFactory import MVCFactory
from kolekti.mvc.controllerfactory import ControllerFactory as CF
from kolekti.http.httprequest import FakeRequest

class BatchModelFactory(MVCFactory):
    def __init__(self, prj):
        self.project = prj

    def __call__(self, name):
        http=FakeRequest('GET', '/projects/%s/' % self.project)
        model=self._loadMVCobject_(name,http)
        try:
            http.setdata('kolekti', 'project', model.project)
        except:
            pass
        return model

def get_model(method, path):
    """
    Ask all routing stuff for the right model
    for a given http method and path
    """

    http=FakeRequest(method, path)
    cf=CF()
    for c in cf.getControllers(http):
        pass
    return c.model

# Projects manager class
class ProjectsManager(object):

    def __init__(self):
        self.dbbackend = SQLAlchemyBackend()
        self.dbbackend.connect()

    def exportprojects(self, lprojects):
        if(len(lprojects) == 0):
            raise Exception, "No project directory found"

        for project in lprojects:
            print "Export project %s" %project
            project = project.decode(LOCAL_ENCODING)

            factory = BatchModelFactory(project)
            adminmodel = factory("AdminModel")

            try:
                Projects = self.dbbackend.get_model('Projects')
                prj = self.dbbackend.select(Projects, "directory = '%s'" %project)[0]
                zipname = adminmodel.archiveProject(prj.id)
                print "--Success to export project"
            except:
                print "--Failed to export project"

    def importprojects(self, lprojectspath):
        factory = BatchModelFactory(None)
        adminmodel = factory("AdminModel")

        for projectpath in lprojectspath:
            zipname = projectpath.split(os.sep)[-1]
            print "Import project %s" %zipname
            try:
                zip = zipfile.ZipFile(projectpath)
                projectdata = zip.read("projectdb.data")
                (name, directory, description, lang) = self.__get_zip_db_project(projectdata)

                pid = adminmodel.newProject(name, directory, description, lang)
                if pid == 0:
                    raise Exception, "Project already exist"

                outpath = os.path.join(conf.get('basedir'), "projects", directory.encode(LOCAL_ENCODING))
                decoutpath = outpath.decode(LOCAL_ENCODING)

                zip.extractall(decoutpath)
                os.remove(os.path.join(outpath, "projectdb.data"))

                client=pysvn.Client()
                for filename in os.listdir(outpath):
                    curpath = os.path.join(decoutpath, filename)
                    if filename in (".svn", "publications", "masters"):
                        continue
                    client.add(curpath, force=True)
                client.checkin([decoutpath],"Import project")
                adminmodel.abstractIO.updateProject(directory)

                self.__set_db_data(pid, projectdata)
                print "--Success to import project"
            except:
                import traceback
                print traceback.format_exc()
                print "--Failed to import project"

    def close(self):
        self.dbbackend.close()

    def __get_zip_db_project(self, projectdata):
        projectdata = projectdata.decode("utf-8")
        line = projectdata.split('\n')
        for l in line:
            pdata = l.split('|')
            if pdata[0] == "Projects":
                return pdata[2:]
        return None

    def __set_db_data(self, pid, projectdata):
        projectdata = projectdata.decode("utf-8")
        line = projectdata.split('\n')
        for l in line:
            pdata = l.split('|')
            if (len(pdata) < 2):
                continue
            (table, obj) = (pdata[0], pdata[1:])

            Table = self.dbbackend.get_model(table)
            if table == "Criterias":
                print "--Add Criterias %s" %l
                d = Table(pid, obj[2], obj[3], obj[4])
                try:
                    self.dbbackend.insert(d)
                except:
                    print "----Failed added Criterias %s" %l
                    self.dbbackend.rollback()
                    continue

                CriteriaValues = self.dbbackend.get_model('CriteriaValues')
                for cl in line:
                    cdata = cl.split('|')
                    if cdata[0] == u"CriteriaValues" and obj[0] == cdata[2]:
                        print "----Add CriteriasValues %s" %cl
                        critval = CriteriaValues(d.id, cdata[3], cdata[4])
                        try:
                            self.dbbackend.insert(critval)
                        except:
                            print "------Failed added CriteriasValues %s" %cl
                            self.dbbackend.rollback()
            elif table == "MasterFilter":
                print "--Add MasterFilter %s" %l
                d = Table(pid, obj[2])
                try:
                    self.dbbackend.insert(d)
                except:
                    print "----Failed added MasterFilter %s" %l
                    self.dbbackend.rollback()

""" SVNSync class """
class SVNProjectsSync(object):
    def __init__(self, repos, *args, **kwargs):
        locale.setlocale(locale.LC_ALL, "fr_FR.UTF8")
        self.repository = repos
        self.model = None
        self.projects = {}

    def update(self):
        ''' update svn project(s) workspace '''
        for l in sys.stdin.readlines():
            if l != '':
                l = l.strip()
                type = l[0]
                path = l[2:].split(' (')[0]
                repospath = self.repository + path
                reposurl = self.__path2url(repospath)
                if type == "A":
                    # add action
                    print 'add', reposurl
                    self.model = get_model("PUT", reposurl)
                    self.model.add(reposurl)
                elif type == "M":
                    # merge action
                    print 'merge', reposurl
                    self.model =  get_model("PUT", reposurl)
                    self.model.merge(reposurl)
                elif type == "D":
                    # delete action
                    print 'delete', reposurl
                    self.model =  get_model("DELETE", reposurl)
                    self.model.delete(reposurl)
                prj = reposurl.split('/')[2]
                # check if project already update
                if not self.projects.get(prj, False):
                    self.model.abstractIO.updateProject(reposurl.split('/')[2])
                    self.projects.update({prj: True})

    def __path2url(self, path):
        ''' Convert path to url '''
        return '/'.join(path[len(conf.get('basedir')):].split(os.sep))



if __name__ == '__main__':
    usage = "usage: %prog -c commande [arguments]"
    parser = OptionParser()


    parser.add_option("-c", "--command", help="The command to perform to kolekti",
                      dest="cmd", default=None, action="store")

    group=OptionGroup(parser,"run : starts kolekti server")
    parser.add_option_group(group)
    group.add_option("-P", "--port", help="Server Port",
                      dest="run_port", default=None, action="store")
    group.add_option("-H", "--host", help="Server Ip to listen",
                      dest="run_host", default=None, action="store")

    group=OptionGroup(parser,"bootstrap : copies web library into server_root space","This commands takes no argument")
    parser.add_option_group(group)

    group=OptionGroup(parser,"syncdb : creates tables in database","This commands takes no argument")
    parser.add_option_group(group)

    group=OptionGroup(parser,"syncmodelsdb : migrate current database schema to application database schema","This commands takes no argument")
    parser.add_option_group(group)

    group=OptionGroup(parser,"exportprojects : export projects data","This commands takes one argument or more: projects directories")
    parser.add_option_group(group)

    group=OptionGroup(parser,"importprojects : import projects data","This commands takes one or more argument: projects ZIP files paths")
    parser.add_option_group(group)

    group=OptionGroup(parser,"syncprojectsvn : sync projects kolekti with repository","This commands takes one or more argument : project directory")
    parser.add_option_group(group)

    group=OptionGroup(parser,"adduser : creates a new user","This commands registers a new user in the database")
    group.add_option("-p", "--project", help="The project to which the user is associated",
                      dest="new_user_project", default=None, action="store")
    group.add_option("-u", "--user", help="User informations : login, password, firstname, lastname, email, organization",
                      dest="new_user", default=None, action="store", nargs=6)
    group.add_option("-a", "--admin", help="User is admin",
                      dest="new_user_is_admin", default=False, action="store_true")
    group.add_option("-t", "--translator", help="User is translator",
                      dest="new_user_is_translator", default=False, action="store_true")

    parser.add_option_group(group)


    group=OptionGroup(parser,"attachuserproject : attach the given user to the given project","this command adds a user to a project")
    group.add_option('-U', '--User', help='user to add to the project',
                        dest='user_to_attach', default=None, action='store')
    group.add_option('-R', '--Project', help='project to add the user to',
                        dest='project_to_be_attached', default=None, action='store')
    parser.add_option_group(group)


    (options, args) = parser.parse_args()

    if options.cmd == "bootstrap":
        from kolekti.bootstrap import BootstrapLib
        bootstrap = BootstrapLib()
        bootstrap.copy_libs()
        bootstrap.copy_base_template()

    if options.cmd == "syncdb":
        try:
            DBbackend=SQLAlchemyBackend()
            DBbackend.connect()
            DBbackend.create_tables()
        except:
            import traceback
            print traceback.format_exc()


    if options.cmd == "syncmodelsdb":
        try:
            DBbackend=SQLAlchemyBackend()
            DBbackend.connect()
            DBbackend.upgrade_models()
        except:
            import traceback
            print traceback.format_exc()

    if options.cmd == "exportprojects":
        prjmanager = ProjectsManager()
        prjmanager.exportprojects(args)
        prjmanager.close()

    if options.cmd == "importprojects":
        prjmanager = ProjectsManager()
        prjmanager.importprojects(args)
        prjmanager.close()

    if options.cmd == "syncprojectsvn":
        svn = SVNProjectsSync(args[0])
        try:
            svn.update()
        except:
            import traceback
            print traceback.format_exc()

    if options.cmd == "adduser":
        factory = BatchModelFactory(options.new_user_project)
        usermodel = factory('UserAccountModel')
        uid = usermodel.create_user(options.new_user[0],
                                  options.new_user[1],
                                  firstname=options.new_user[2],
                                  lastname=options.new_user[3],
                                  email=options.new_user[4],
                                  organization=options.new_user[5],
                                  admin=options.new_user_is_admin,
                                  translator=options.new_user_is_translator)
        print 'User', options.new_user[0], "created with uid", uid
        if options.new_user_project is not None:
            admmodel = factory('AdminModel')
            admmodel.attach_userprojects(uid,[options.new_user_project])

    if options.cmd == 'attachuserproject':
        print 'attaching'
        factory = BatchModelFactory(None)
        usermodel = factory('UserAccountModel')
        print 'uid = usermodel.get_user_id(%s)' % options.user_to_attach
        uid = usermodel.get_user_id(options.user_to_attach)
        print 'userid = %s' % uid
        admmodel = factory('AdminModel')
        print "admmodel.attach_userprojects(%s,[%s])" % (uid, options.project_to_be_attached)
        admmodel.attach_userprojects(uid,[options.project_to_be_attached])

    if options.cmd == "run":
        from kolekti.http.wsgirequesthandler import KolektiHandlerFct
        from paste import httpserver
        if options.run_host is not None:
            host = options.run_host
        else:
            host = conf.get('host')
        if options.run_port is not None:
            port = options.run_port
        else:
            port = str(conf.get('port'))

        httpserver.serve(KolektiHandlerFct,
                     host=host,
                     port=port)
