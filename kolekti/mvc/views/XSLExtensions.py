# -*- coding: utf-8 -*-
#
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

""" classes for functions extensions for xslt processor in views"""
__author__ = "bonhomme"
__date__ = "$Jul 16, 2009 4:37:46 PM$"

import urllib2
import hashlib
import os
import time
import re
from datetime import datetime

from pytz import common_timezones
from babel.dates import format_date, format_datetime
from lxml import etree as ET

from kolekti.kolekticonf import conf
from kolekti.mvc.MVCFactory import MVCobject
#from kolekti.utils.userdata.sessionservice import SessionService
#from kolekti.utils.userdata.profileservice import ProfileService
#from kolekti.utils.userdata.lockservice import LockService
from kolekti.mvc.models.SessionModel import SessionModel
from kolekti.mvc.models.ProfileModel import ProfileModel

from kolekti.logger import debug,dbgexc
from kolekti.utils.i18n.i18n import tr

class KExtensions(MVCobject):
    def __init__(self, hr, model):
        super(KExtensions,self).__init__(hr)
        self.http = hr
        self.model = model
        if (conf.get('sessionservice')):
            self.session=SessionModel(hr)
        if (conf.get('profileservice')):
            self.profile=ProfileModel(hr)
        if (conf.get('lockservice')):
            self.lock=LockService()

#Xpath functions

class KFunctions(KExtensions):
    ens = "kolekti:extensions:functions"

    def userid(self, _):
        try:
            return self.http.userId
        except:
            return ''

    def admin(self, _):
        return self.http.admin

    def translator(self, _):
        return self.http.translator

    def gettext(self, _, *args):
        msg = args[0].strip()
        params = {}
        for p in re.findall("%\([^)]+\)s", msg):
            code = p[2:-2]
            params[code] = "\%("+code+")s"
        s = tr(unicode(msg), params)
        return s.i18n(self.http.translation)

    def getlocale(self, _):
        locale = self.http.getdata("user", "locale")
        if locale is None:
            locale = conf.get("locale_default")
        return locale

    def getlocalelist(self, _):
        confxml = ET.parse(os.path.join(conf.confdir, 'config.xml'))
        r = []
        for lang in confxml.xpath('/config/locale/lang'):
            r.append(lang)
        return r

    def gettimezonelist(self, _):
        r = []
        for tz in common_timezones:
            r.append(ET.Element("utc", {"label": tz, "value": tz}))
        return r

    def replace_param(self, _, *args):
        query = args[0].strip()
        name = args[1].strip()
        value = args[2].strip()
        return query.replace(u"\%("+name+u")s", value)

    def kolekticonf(self, _, *args):
        try:
            v = conf.get(args[0])
            return v
        except:
            return ''

    def selfpath(self, _):
        return self.http.path

    def selfhashuri(self, _, *args):
        url=args[0]
        return hashlib.md5(url).hexdigest()

    def urlquote(self, _, *args):
        url=args[0]
        return urllib2.quote(url.encode('utf-8'))

    def urlunquote(self, _, *args):
        url=args[0]
        return urllib2.unquote(url).decode('utf-8')

    def url2id(self, _, url):
        return self.model.url2id(url)

    def id2url(self, _, id):
        return self.model.id2url(unicode(id))

    def normalize_id(self, _, *args):
        id=self.urlunquote(_, *args)
        return self.model.abstractIO.normalize_id(id)

    def get_session_value(self, _, *args):
        try:
            key=":".join(self.http.sessionId,args[0])
            p=self.session.userdata.getParam(self.http.userId, key)
            if p is None:
                return []
            ke=ET.Element('{kolekti:ctrdata}value')
            ke.set('id',key)
            ke.text=unicode(p)
            return [ke]
        except:
            return []

    def get_profile_value(self, _, *args):
        try:
            key=args[0]
            p=self.profile.userdata.getParam(self.http.userId,key)
            if p is None:
                return []
            ke=ET.Element('{kolekti:ctrdata}value')
            ke.set('id',key)
            ke.text=unicode(p)
            return [ke]
        except:
            return ''

    def get_http_data(self, _, *args):
        try:
            ns=args[0]
            name=args[1]
            return self.http.getdata(ns, name)
        except:
            return None

    def get_params_value(self, _, *args):
        try:
            param=args[0]
            return self.http.params.get(param, None)
        except:
            return None

    def listtemplates(self, _, *args):
        try:
            resid=self.urlunquote(_, *args)
            res = []
            for tpl in self.model.listCollection(resid):
                res.append(ET.Element('{kolekti:ctrdata}option', {'value': tpl}))
            return res
        except:
            return []

    def format_time(self, _, *args):
        try:
            lang = self.http.getdata('user', 'locale')
            ts = float(args[0])
            dt=datetime.utcfromtimestamp(ts)
            fdt = format_datetime(dt, tzinfo=self.model.tzinfo, locale=lang)
            return fdt
        except:
            dbgexc()
            return args[0]
        
    def get_svn_revision(self, _, *args):
        res = []
        try:
            try:
                path = args[0]
                if path == '':
                    raise
            except:
                path = self.http.path

            try:
                limit = int(args[1])
            except:
                limit = 0
            svnIO=self._loadMVCobject_('svnIO')
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
