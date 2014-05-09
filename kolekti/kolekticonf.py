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


import imp
import os
import sys
import re

import lxml.etree as ET

#from kolekti.logger import dbgexc

# configuration default values / path to values in config file
# entries are 3-tuples: default_value, xpath, xpath_type,

__conf__ = {
    'version':(u'0.6r','/config/@version','string'),

    'host':(u'127.0.0.1','/config/server/@host', 'string'),
    'port':(u'8000','/config/server/@port', 'string'),
    'routesdef':(u'_CONFDIR_/routes.xml','/config/server/@routes','path'),

    'localedir': (u'_CONFDIR_/locale', '/config/localedir/@path', 'path'),
    'basedir':(u'_APPDIR_/server_root','/config/basedir/@path', 'path'),
    'tmpdir':(u'/tmp','/config/tmpdir/@path','path'),

    'db_type':(u'mysql','/config/database/@type', 'string'),
    'db_fmk_model':(u'fmk_db_models','/config/database/@model', 'string'),
    'db_app_model':(u'db_models','/config/database/@app_model', 'string'),
    'db_host':(u'127.0.0.1','/config/database/@host', 'string'),
    'db_login':(u'kolekti','/config/database/@login', 'string'),
    'db_passwd':(u'kolekti','/config/database/@password', 'string'),
    'db_base':(u'kolekti','/config/database/@db', 'string'),

    'svn':(False,'/config/svn','boolean'),
    'svn_passwdfile':(u'_CONFDIR_/passwdfile','/config/svn/@passwdfile','path'),
    'svn_groupfile':(u'_CONFDIR_/groupfile','/config/svn/@groupfile','path'),

    'mail_host':(u'localhost','/config/mail/@host','string'),
    'mail_port':(u'25','/config/mail/@port','string'),
    'mail_address':(u'noreply@yourdomain','/config/mail/@sender_address', 'string'),

    'authmodel':(u'AuthModel','/config/auth/@model','string'),
    'sessionservice':(False,'/config/sessionservice','boolean'),
    'profileservice':(False,'/config/profileservice','boolean'),
    'profileNs':(u'http://www.kolekti.org/profiles','/config/profileservice/@namespace','string'),
    'lockservice':(False,'/config/lockservice','boolean'),
    'locksfile':(u'/tmp/kolekti.locks','/config/lockservice/@locksfile','string'),

    'locale_default':(u'fr','/config/locale/@default','string'),
    'locale_domain':(u'kolekti','/config/locale/@domain','string'),

    'debug':(False,'/config/debug','boolean'),
    'debug_locale':(False,'/config/debug_locale','boolean'),
    'verbosity':(u'verbose','/config/debug/@level','string'),

    'nodejs':(u'node','/config/nodejs','string'),
    'lessc':(u'lessc','/config/lessc','string'),

#    'projectroles':{'manager':'gestionnaire'},


}
revdir = {}

LOCAL_ENCODING=sys.getfilesystemencoding()


def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


class KConf(object):
    confdir="/etc/kolekti"

    def __init__(self,confdict):
        # try in /etc/kolekti/
        self.__c=confdict
        self.__c.update({'fmkdir':(get_main_dir(),)})
        self.__c.update({'appdir':(os.environ['KOLEKTI_APPDIR'],)})
        self.__c.update({'app':(os.environ['KOLEKTI_APP'],)})
        self.__getconfdir()
        self.__c.update({'confdir':(self.confdir,)})
        try:
            self.__confxml=ET.parse(os.path.join(self.__c['confdir'][0],'config.xml'))
        except:
            self.__confxml=ET.Element('fake')
        
        self.mvcpathlist=[]
        self.sqlpathlist=[]
        self.__getmvcpathes()
        self.__getsqlpathes()
        self.__getroutes()

    def __getconfdir(self):
        # Environement variable

        # KOLEKTI_APPDIR
        confdir=os.path.join(os.environ['KOLEKTI_APPDIR'],'config')
        if os.path.isfile(os.path.join(confdir, 'config.xml')):
            self.confdir=confdir
            return

        # KOLEKTI_APP -> /etc/kolekti/KOLEKTI_APP/
        confdir=os.path.join('/','etc','kolekti',os.environ['KOLEKTI_APP'])
        if os.path.isfile(os.path.join(confdir, 'config.xml')):
            self.confdir=confdir
            return
        # default is /etc/kolekti (default class attribute)
        
    def __getroutes(self):
        try:
            routes=ET.parse(self.get('routesdef'))
            self.__c.update({'routes':(RouteNode(routes.getroot()),)})
        except:
            import traceback
            print traceback.format_exc()

    def __getmvcpathes(self):
        # Set pathes to search in when loading mvc object
        # first search in the app
        self.mvcpathlist.append(os.path.join(self.__c['appdir'][0],'ioabstraction'))
        self.mvcpathlist.append(os.path.join(self.__c['appdir'][0],'models'))
        self.mvcpathlist.append(os.path.join(self.__c['appdir'][0],'views'))
        self.mvcpathlist.append(os.path.join(self.__c['appdir'][0],'controllers'))
        #then in the framework
        self.mvcpathlist.append(os.path.join(self.__c['fmkdir'][0],'utils','ioabstraction'))
        self.mvcpathlist.append(os.path.join(self.__c['fmkdir'][0],'mvc','models'))
        self.mvcpathlist.append(os.path.join(self.__c['fmkdir'][0],'mvc','views'))
        self.mvcpathlist.append(os.path.join(self.__c['fmkdir'][0],'mvc','controllers'))

    def __getsqlpathes(self):
        # Set pathes to search in when loading sql object
        self.sqlpathlist.append(os.path.join(self.__c['appdir'][0],'models','sql'))
        self.sqlpathlist.append(os.path.join(self.__c['fmkdir'][0],'mvc','models','sql'))
    
    def get(self,key):
        try:
            (default, xpath, xtype)=self.__c[key]
            if len(self.__confxml.xpath(xpath)):
                if xtype=='path':
                    v = self.__confxml.xpath("string(%s)"%(xpath,))
                else:
                    v = self.__confxml.xpath("%s(%s)"%(xtype, xpath))
            else:
                v = default
            if xtype=='path':
                v=v.encode(LOCAL_ENCODING)
                try:
                    v=v.replace('_APPDIR_', self.__c['appdir'][0])
                    v=v.replace('_FMKDIR_', self.__c['fmkdir'][0])
                    v=v.replace('_CONFDIR_', self.__c['confdir'][0])
                except:
                    pass
            if xtype=='string':
                v=unicode(v)
        except:
            v =  self.__c[key][0]
        return v



class RouteNode(dict):
    def __init__(self,xroute):
        super(RouteNode,self).__init__()
        self.update({'subroutes':[],
                     'conditions':[],
                     'controller':[],
                     'model':[],
                     'io':[],
                     'view':[],
                     'break':False,
                     'name':xroute.get('name')})
        for e in xroute:
            if e.tag=='route':
                self['subroutes'].append(RouteNode(e))
            if e.tag=='match':
                c=[]
                for xhook in e.findall('hook'):
                    attr=dict(xhook.items())
                    t=attr.pop('type')
                    # compile attributes "match" into regular expression
                    try:
                        m=attr.pop('match')
                        attr.update({'match':re.compile(m)})
                    except KeyError:
                        pass

                    hook={'type':t,
                          'args':attr,
                          }
                    c.append(hook)
                self['conditions'].append(c)
            if e.tag in ['controller','view','model','io']:
                self[e.tag].append(e.get('module',e.tag.capitalize()))
            if e.tag=='break':
                self['break']=True


conf=KConf(__conf__)
