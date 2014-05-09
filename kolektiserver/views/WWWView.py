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
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

from lxml import etree as ET

from kolekti.mvc.views.XSLUIView import XSLUIView
from kolekti.mvc.views import XSLExtensions
from kolekti.logger import dbgexc,debug

#from kolekti.mvc.models.sql.models import Users

class WWWView (XSLUIView):
    def _load_extensions(self):
        extf_obj = ViewXSLExtensions(self.http, self.model)
        exts = (n for n in dir(ViewXSLExtensions) if not(n.startswith('_')))
        self.extensions.update(ET.Extension(extf_obj,exts,ns=extf_obj.ens))

class ViewXSLExtensions(XSLExtensions.KFunctions):
    def __init__(self, *args, **kwargs):
        super(ViewXSLExtensions,self).__init__(*args, **kwargs)

    def username(self, _, *args):
        ''' Get username with this uid / or login if uid id -1'''
        try:
            uid = args[0]
        except:
            uid = self.http.userId
            
        try:
            uid=int(uid)
        except:
            uid=None
            
        try:
            userlogin=args[1]
        except:
            userlogin=None

        try:
            sql = self.http.dbbackend
            Users = sql.get_model('Users')
            if uid != -1 and uid is not None:
                user = sql.select(Users, "id='%d'" %uid)
            elif userlogin is not None:
                user = sql.select(Users, "login='%s'" %userlogin)
            u = user[0]
            return "%s %s" %(u.firstname,u.lastname)
        except:
            return 'Kolekti'

    def userid(self, _, *args):
        try:
            userlogin=args[0]
        except:
            userlogin=None
        
        if (userlogin is None):
            try:
                return self.http.userId
            except:
                return ''
        else:
            try:
                sql = self.http.dbbackend
                Users = sql.get_model('Users')
                user = sql.select(Users, "login='%s'" %userlogin)
                u = user[0]
                return str(u.id)
            except:
                return ''

    def userprojects(self, _):
        ''' Get the projects to which the user belongs'''
        model=self._loadMVCobject_('AdminModel')
        projs=model.getUserProjects(self.http.userId)
        res=[]
        for p in projs:
            res.append(p)
        return res

    def hascriteria(self, _, *args):
        try:
            criteria = args[0]
            parser = ET.XMLParser(load_dtd=True)
            data = ET.XML(self.model.abstractIO.getFile(self.http.path),parser)
            res = data.xpath("//h:*[contains(@class,'=') and contains(@class,'%s')]|//h:img[contains(@src, '_%s_')]|//h:var[contains(substring-before(@class, ':'), '_%s_')]" %(criteria, criteria, criteria), namespaces={"h": "http://www.w3.org/1999/xhtml"})
        except:
            return False
        return len(res) > 0

    def getcriterias(self, _):
        model=self._loadMVCobject_('ConfigurationModel')
        return model.getCriterias()

    def getpubscripts(self, _):
        model=self._loadMVCobject_('ProjectModel')
        return model.getProjectPubscripts()

    def getmasterfilters(self, _):
        res = []
        try:
            pid = int(self.model.project.get('id'))
            sql = self.http.dbbackend
            MasterFilter = sql.get_model('MasterFilter')
            mcrits = sql.select(MasterFilter, "pid=%d" %pid)
            for mc in mcrits:
                res.append(ET.Element("masterfilter", {"id": str(mc.id), "pid": str(mc.pid), "value": mc.value}))
        except:
            dbgexc()
            pass
        return res

    def get_svn_revision(self, _, *args):
        res = []
        try:
            try:
                path = args[0]
                if path == '':
                    raise
            except:
                path = u'@'

            try:
                limit = int(args[1])
            except:
                limit = 0
            svnIO=self._loadMVCobject_('svnProjectsIO')
            for log in svnIO.svnlog(path, limit):
                attrib = {}
                for (key, value) in log.iteritems():
                    if type(value) != unicode:
                        value = str(value)
                    attrib[key] = value
                res.append(ET.Element("rev", attrib))
        except:
            dbgexc()
        return res

    def validmod(self, _, *args):
        modmodel = self._loadMVCobject_('ModulesModel')
        return modmodel.isValid(unicode(args[0]))
