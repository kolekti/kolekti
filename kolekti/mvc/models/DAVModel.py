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




""" model : DAV class"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import urllib2
import time

from lxml import etree as ET
from wsgiref.handlers import format_date_time

from kolekti.mvc.models.Properties import Properties
from kolekti.mvc.models.Model import Model
from kolekti.exceptions import exceptions as EXC
from kolekti.utils.locking.lockservice import LockService
from kolekti.kolekticonf import conf

class DAVModel(Model,Properties):
    HASLOCK=False
    __localNS={'DAV:':'dav'}

    def __init__(self, *args, **kwargs):
        Model.__init__(self, *args)
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        Properties.__init__(self,*args,**kwargs)

    def listCollection(self, resid, ignore_patterns=('_','~','.')):
        l=[f for f in self.abstractIO.getDir(resid) if not (f.split('/')[-1].startswith(ignore_patterns) or f.endswith(ignore_patterns))]
        l.sort()
        return l

    def getpropval(self, resid, propname, ns='DAV:'):
        return super(DAVModel, self).getpropval(resid, propname, ns)

    def _xmlprop(self, name, ns="DAV:"):
        return super(DAVModel, self)._xmlprop(name,ns)

    #Default DAV Properties

    def _prop_dav_creationdate(self, resid):
        #1997-12-01T17:42:21-08:00
        # we use utc for datetimes => 1997-12-02T01:42:21Z
        p = self._xmlprop('creationdate')
        try:
            # date-time (defined in [RFC3339], see the ABNF in Section 5.6.)
            ts = self.abstractIO.getCreationDate(resid)
            p.text = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)).decode('utf8')
            #p.text = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ts)).decode('utf8')
        except AttributeError:
            raise EXC.NotFound
        return p

    def _prop_dav_checkedin(self, resid):
        p = self._xmlprop('checked-in')
        #p.text = uri.objname
        p.text = resid.split('/')[-1]
        return p

    def _prop_dav_checkedout(self, resid):
        p = self._xmlprop('checked-out')
        #p.text = uri.objname
        p.text = resid.split('/')[-1]
        return p

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        p.text = resid.split('/')[-1]
        return p

    def _prop_dav_resourcetype(self, resid):
        p = self._xmlprop('resourcetype')
        if self.isCollection(resid):
            ET.SubElement(p, "{DAV:}collection")
        return p

    def _prop_dav_getcontentlanguage(self, resid):
        p = self._xmlprop('getcontentlanguage')
        p.text = 'en'
        return p

    def _prop_dav_getcontentlength(self, resid):
        p = self._xmlprop('getcontentlength')
        p.text = str(self.abstractIO.getSize(resid))
        return p

    def _prop_dav_getcontenttype(self, resid):
        p = self._xmlprop('getcontenttype')
        if self.isCollection(resid):
            p.text="httpd/unix-directory"
        else:
            (t, e) = self.abstractIO.getContentType(resid)
            p.text = t
        return p

    def _prop_dav_getetag(self, resid):
        fp = self._etag(resid)
        p = self._xmlprop('getetag')
        p.text = fp
        return p

    def _prop_dav_getlastmodified(self, resid):
        #rfc1123-date (defined in Section 3.3.1 of [RFC2616])
        p = self._xmlprop('getlastmodified')
        ts = self.abstractIO.getUpdateDate(resid)
        #p.text = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ts)).decode('utf8')
        p.text = format_date_time(ts)
        return p

    def _prop_dav_supportedlock(self, resid):
        p = self._xmlprop('supportedlock')
        if self.HASLOCK:
            lckentry = ET.SubElement(p, "{DAV:}lockentry")
            lckscope = ET.SubElement(lckentry, "{DAV:}lockscope")
            ET.SubElement(lckscope, "{DAV:}exclusive")
            lcktype = ET.SubElement(lckentry, "{DAV:}locktype")
            ET.SubElement(lcktype, "{DAV:}write")
        return p

    def _prop_dav_lockdiscovery(self, resid):
        p = self._xmlprop('lockdiscovery')
        if self.HASLOCK:
            lock = self.abstractIO.get_lock(resid)
            if lock is not None:
                p.append(self._info_lock(lock))
        return p

    def _prop_dav_versionname(self, resid):
        p = self._xmlprop('version-name')
        #p.text = uri.objname
        p.text = resid.split('/')[-1]
        return p

    def create_lock(self, resid, uid, timeout, depth, body):
        lock = self.abstractIO.lock_file(resid)
        if lock is None:
            self.__lock_exception(resid)
        return (lock['token'], self.__lock_discovery(lock))

    def refresh_lock(self, resid, token):
        lock = self.abstractIO.refresh_lock_file(resid, token)
        if lock is None:
            self.__lock_exception(resid)
        return (lock['token'], self.__lock_discovery(lock))

    def release_lock(self, resid, token):
        unlock = self.abstractIO.unlock_file(resid, token)
        return unlock

    def __lock_discovery(self, lock):
        ldocelem = ET.Element("{DAV:}prop")
        ldoc = ET.ElementTree(ldocelem)
        lde = ET.SubElement(ldocelem, "{DAV:}lockdiscovery")
        lde.append(self._info_lock(lock))
        return ldoc

    def __lock_exception(self, resid):
        ldocelem = ET.Element("{DAV:}multistatus")
        ldoc = ET.ElementTree(ldocelem)
        ldr = ET.SubElement(ldocelem, "{DAV:}response")
        ldh = ET.SubElement(ldr, "{DAV:}href")
        ldh.text=resid
        lds = ET.SubElement(ldr, "{DAV:}status")
        lds.text="HTTP/1.1 423 Locked"
        ldr = ET.SubElement(ldocelem, "{DAV:}response")
        ldh = ET.SubElement(ldr, "{DAV:}href")
        ldh.text=resid
        lds = ET.SubElement(ldr, "{DAV:}status")
        lds.text="HTTP/1.1 424 Failed Dependency"
        raise EXC.Multistatus, ET.tostring(ldoc)

    def _info_lock(self, lock):
        """ builds the lock properties xml instance """
        linfo = ET.Element("{DAV:}activelock")
        #insert the lock type element
        ltype = ET.SubElement(linfo, "{DAV:}locktype")
        ET.SubElement(ltype, "{DAV:}write")
        lscope = ET.SubElement(linfo, "{DAV:}lockscope")
        ET.SubElement(lscope, "{DAV:}exclusive")
        ldepth = ET.SubElement(linfo, "{DAV:}depth")
        ldepth.text = "0"

        lowner = ET.SubElement(linfo, "{DAV:}owner")
        if lock["owner"].startswith("http"):
            lownerval = ET.SubElement(lowner, "{DAV:}href")
            lownerval.text = lock["owner"]
        else:
            lowner.text = lock["owner"]

        #insert the lock timeout
        ltime = ET.SubElement(linfo, "{DAV:}timeout")
        ltime.text = "Infinite"

        #insert the lock token
        ltoken = ET.SubElement(linfo, "{DAV:}locktoken")
        ltokenref = ET.SubElement(ltoken, "{DAV:}href")
        ltokenref.text = lock["token"]
        return linfo
