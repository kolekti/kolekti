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


""" sessionservice module
This module contains the services for management of locks

"""
__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import uuid
import re

from time import time
from lxml import etree as ET
from threading import Lock as ExclLock
from lock import Lock
from constants import LOCK_DEPTH_ZERO, LOCK_DEPTH_INFINITE
from constants import LOCK_SCOPE_EXCLUSIVE, LOCK_SCOPE_SHARED
from constants import LOCK_TYPE_WRITE
from constants import LOCK_SEARCH_RESOURCE, LOCK_SEARCH_ANCESTORS, LOCK_SEARCH_DESCENDANTS, LOCK_SEARCH_PARENT

from kolekti.logger import debug,dbgexc
from kolekti.exceptions import exceptions as EXC

class LockService(object):

    __lock=ExclLock()
    #__shared_state = {}
    # Borg Pattern all LockService Objects share the same state
    def __init__(self, model):
        #self.__dict__ = self.__shared_state
        self.model = model

    # Public Methods

    def initService(self, locksfile):
        self.__locksfile = locksfile
        self.__lockedResources = {}
        self.__locks = {}
        try:
            self.__loadlocks()
        except:
            dbgexc()

    def createLock(self, resid, uid, timeout, depth, body):
        # Get the timeout
        if timeout and timeout != "Infinite":
            timeout = int(timeout.split("-")[1])
        else:
            timeout = Lock.INFINITE_TIMEOUT

        # Get the depth O or infinity (default)
        if depth:
            d = depth
            if d=="0":
                depth=0
            elif d=="infinity":
                depth=LOCK_DEPTH_INFINITE
            else:
                raise EXC.PreconditionFailed
        else:
            depth = LOCK_DEPTH_INFINITE

        try:
            (lockowner, lockscope, locktype) = self._parseLock(body)
        except:
            dbgexc()
            raise EXC.PreconditionFailed

        # check if the resource is lockable
        try:
            # is there an exclusive lock on the resource itself 
            locks=self.getLocks(resid,scope=LOCK_SCOPE_EXCLUSIVE)
            if len(locks) > 0:
                print resid, 'all ready lock'
                raise EXC.Locked

            if lockscope==LOCK_SCOPE_EXCLUSIVE:
                searchscope=LOCK_SCOPE_EXCLUSIVE|LOCK_SCOPE_SHARED
            else:
                searchscope=LOCK_SCOPE_EXCLUSIVE

            # is there an lock in ancestors collections with depth=infinity => 423+424
            locks=self.getLocks(resid,where=LOCK_SEARCH_ANCESTORS,  scope=searchscope, depth=LOCK_DEPTH_INFINITE)
            if locks:
                raise EXC.Locked

            # if ask an infinite-depth lock, is there a lock in descendant resources  => 423+424
            if self.model.isCollection(resid) and depth == LOCK_DEPTH_INFINITE:
                locks=self.getLocks(resid,where=LOCK_SEARCH_DESCENDANTS,  scope=searchscope)
                if locks:
                    raise EXC.Locked
        except EXC.Locked:
            #build a multistaus 
            ldocelem = ET.Element("{DAV:}multistatus")
            ldoc = ET.ElementTree(ldocelem)
            ldr = ET.SubElement(ldocelem, "{DAV:}response")
            ldh = ET.SubElement(ldr, "{DAV:}href")
            ldh.text=self.getResource(locks[0])
            lds = ET.SubElement(ldr, "{DAV:}status")
            lds.text="HTTP/1.1 423 Locked"
            ldr = ET.SubElement(ldocelem, "{DAV:}response")
            ldh = ET.SubElement(ldr, "{DAV:}href")
            ldh.text=resid
            lds = ET.SubElement(ldr, "{DAV:}status")
            lds.text="HTTP/1.1 424 Failed Dependency"
            raise EXC.Multistatus, ET.tostring(ldoc)

        """ create a new lock on a resource """
        token = self.lockResource(resid, uid, lockowner, depth, lockscope, locktype, timeout)

        #Build result
        if token is not None:
            ldocelem = ET.Element("{DAV:}prop")
            ldoc = ET.ElementTree(ldocelem)
            lde = ET.SubElement(ldocelem, "{DAV:}lockdiscovery")
            lde.append(self._infoLock(token))
            
            return (token, ldoc)
        else:
            raise EXC.Conflict


    def refreshLock(self, resid, locktoken, timeout):
        locks=self.__lockedResources.get(resid,None)
        for l in locks:
            if l.token.urn[9:]==locktoken:
                self.__lock.acquire()
                if timeout and timeout != "Infinite":
                    timeout = int(timeout.split("-")[1])
                else:
                    timeout = Lock.INFINITE_TIMEOUT
                l.refresh(timeout)
                self.__flushlocks()
                self.__lock.release()
                ldocelem = ET.Element("{DAV:}prop")
                ldoc = ET.ElementTree(ldocelem)
                lde = ET.SubElement(ldocelem, "{DAV:}lockdiscovery")
                lde.append(self._infoLock(locktoken))
                return (l.token.urn[9:], ldoc)
        return None

    def lockResource(self,resid,uid,owner,depth,scope,locktype,timeout):
        """ locks a resource or collection
        Locks the resource or collection identified by resid
        uid   : principal that creates the lock
        owner : dict containing owner info (keys : uri, text)
        depth : lock depth
        scope : LOCK_SCOPE_EXCLUSIVE or LOCK_SCOPE_SHARED
        timeout : timeoutvalue in s
        """

        self.__lock.acquire()
        self.__checkTimeout()


        # get new lock

        lock = Lock(uid, owner, depth=depth, scope=scope, timeout=timeout, locktype=locktype)
        # register the lock
        self.__locks[lock.token.urn[9:]] = lock
        try:
            self.__lockedResources[resid].append(lock)
        except:
            self.__lockedResources[resid] = [lock]
        # self.flush()
        self.__flushlocks()
        self.__lock.release()
        return lock.token.urn[9:]

    def releaseLock(self,resid, locktoken):
        """ realeases a resource or collection
        """
        self.__lock.acquire()
        self.__checkTimeout()
        # iter over the locked resources
        remres = []
        for (r, lt) in self.__lockedResources.iteritems():
            # get the list of the remaining locks after release
            nt = [t for t in lt if (t.token.urn[9:]) != locktoken]
            if len(nt):
                # there are remaining locks on the resource
                self.__lockedResources[r] = nt
            else:
                # no more locks on this resource
                remres.append(r)
        for r in remres:
            self.__lockedResources.pop(r)
        # release the lock object
        self.__locks.pop(locktoken)
        self.__flushlocks()
        self.__lock.release()


    def checkLock(self, token, principal):
        self.__lock.acquire()
        self.__checkTimeout()
        self.__lock.release()
        try:
            return self.__locks[token].principal==principal
        except KeyError:
            return False

    def getLocks(self,resid,
                 where=LOCK_SEARCH_RESOURCE,
                 scope=(LOCK_SCOPE_EXCLUSIVE|LOCK_SCOPE_SHARED),
                 depth=(LOCK_DEPTH_ZERO|LOCK_DEPTH_INFINITE),
                 type=LOCK_TYPE_WRITE):
        """ searches a list of lock tokens for a resource (excluding locks on parent collections)
        """
        debug("LOCK   GET LOCKS %s %s %s %s" %(resid,scope,depth,type))
        self.__lock.acquire()
        self.__checkTimeout()
        self.__lock.release()
        collected=[]
        if where & LOCK_SEARCH_RESOURCE:
            try:
                collected.extend(self.__lockedResources[resid])
            except KeyError:
                pass
        debug("LOCK   COLLECTED RES %s" %collected)
        if where & LOCK_SEARCH_PARENT:
            ll=[l for (u,l) in self.__lockedResources.iteritems() if is_parent(u,resid)]
            try:
                l=reduce(lambda a,b:a+b,ll)
            except:
                l=[]
            collected.extend(l)
        elif where & LOCK_SEARCH_ANCESTORS:
            ll=[l for (u,l) in self.__lockedResources.iteritems() if is_prefix(u,resid)]
            try:
                l=reduce(lambda a,b:a+b,ll)
            except:
                l=[]
            collected.extend(l)
        debug("LOCK   COLLECTED ANCEST %s" %collected)
        if where & LOCK_SEARCH_DESCENDANTS:
            ll=[l for (u,l) in self.__lockedResources.iteritems() if is_prefix(resid,u)]
            try:
                l=reduce(lambda a,b:a+b,ll)
            except:
                l=[]
            collected.extend(l)

        debug("LOCK   COLLECTED DESCENT %s" %collected)

        collected=[l for l in collected if l.scope&scope]
        if depth != LOCK_DEPTH_ZERO:
            collected=[l for l in collected if l.depth&depth]
        collected=[l for l in collected if l.type&type]

        debug("LOCK   FILTERED %s" %collected)
        print collected
        return [l.token.urn[9:] for l in collected]

    def getResource(self,token):
        for (r,ll) in self.__lockedResources.iteritems():
            for l in ll:
                if l.token.urn[9:]==token:
                    return r

    def isExclusive(self,token):
        return self.__locks[token].scope==LOCK_SCOPE_EXCLUSIVE

    def getLockInfo(self,token):
        l = self.__locks[token]
        return {'owner':l.owner, 'depth':l.depth, 'scope':l.scope, 'type':l.type, 'timeout':l.timeout}

    # Protected methods

    def _infoLock(self, lockToken):
        """ builds the lock properties xml instance """
        linfo = ET.Element("{DAV:}activelock")
        lock = self.getLockInfo(lockToken)
        #insert the lock type element
        if lock.has_key('type'):
            ltype = ET.SubElement(linfo, "locktype")
            if lock['type'] == LOCK_TYPE_WRITE:
                ET.SubElement(ltype, "{DAV:}write")

        #insert the lock scope element
        if lock.has_key('scope'):
            lscope = ET.SubElement(linfo, "{DAV:}lockscope")
            if lock['scope'] == LOCK_SCOPE_EXCLUSIVE:
                ET.SubElement(lscope, "{DAV:}exclusive")
            if lock['scope'] == LOCK_SCOPE_SHARED:
                ET.SubElement(lscope, "{DAV:}shared")

        #insert the lock depth element
        if lock.has_key('depth'):
            ldepth = ET.SubElement(linfo, "{DAV:}depth")
            if lock['depth'] == LOCK_DEPTH_INFINITE:
                ldepth.text = "infinite"
            else:
                ldepth.text = str(lock['depth'])

        #insert the lock owner
        if lock.has_key('owner'):
            owner = lock['owner']
            lowner = ET.SubElement(linfo, "{DAV:}owner")
            if owner.has_key('text') and owner['text']:
                lowner.text = owner['text']
            if owner.has_key('uri'):
                lownerval = ET.SubElement(lowner, "{DAV:}href")
                lownerval.text = owner['uri']

        #insert the lock timeout
        ltime = ET.SubElement(linfo, "{DAV:}timeout")
        if lock.has_key('timeout') and lock['timeout'] != Lock.INFINITE_TIMEOUT:
            ltime.text = str(lock['timeout'])
        else:
            ltime.text = "Infinite"

        #insert the lock tocken
        ltoken = ET.SubElement(linfo, "{DAV:}locktoken")
        ltokenref = ET.SubElement(ltoken, "{DAV:}href")
        ltokenref.text = "opaquelocktoken:%s" % lockToken

        return linfo

    def _parseLock(self, msg):
        doc = ET.ElementTree(ET.fromstring(self.__hackDAVNS(msg)))
        
        # get lock scope
        lockinfo = doc.getroot()
        scope = lockinfo.find('{%s}lockscope' % self.davns)
        if scope.find('{%s}exclusive' % self.davns) is not None:
            lockscope = LOCK_SCOPE_EXCLUSIVE
        elif scope.find('{%s}shared' % self.davns) is not None:
            lockscope = LOCK_SCOPE_SHARED
        else:
            raise EXC.BadRequest
        
        # get lock type (only write)
        type = lockinfo.find('{%s}locktype' % self.davns)
        if type.find('{%s}write' % self.davns) is not None:
            locktype = LOCK_TYPE_WRITE
        else:
            raise EXC.BadRequest
        
        #get lock owner
        lockowner = {}
        owner = lockinfo.find('{%s}owner' % self.davns)
        if owner.find('{%s}href' % self.davns) is not None:
            lockowner['uri'] = owner.find('{%s}href' % self.davns).text
        else:
            lockowner['text'] = owner.text
        return(lockowner, lockscope, locktype)

    # Private methods

    def __loadlocks(self):
        try:
            doc=ET.parse(self.__locksfile)
            self.__unmarshall(doc)
            debug("LOCK   LOADED LOCKS")
            debug("LOCK   LOCKS ARE %s" %self.__locks)
            debug("LOCK   RESOU ARE %s" %self.__lockedResources)
        except IOError:
            sfile = open(self.__locksfile, 'w')
            sfile.write("<lockbase />")
            sfile.close()

    def __flushlocks(self):
        doc = self.__marshall()
        sfile = open(self.__locksfile, 'w')
        sfile.write(ET.tostring(doc))
        sfile.close()

    def __unmarshall(self, doc):
        root=doc.getroot()
        for lock in doc.iter(tag='lock'):
            token=lock.get('token')
            ownerelt = lock.find('owner')
            if ownerelt.get("type") == 'uri':
                owner = {'uri':ownerelt.get("uri")}
            else:
                owner = {'text':ownerelt.get("text")}
            princ = int(lock.get("principal"))
            depth = int(lock.get("depth"))
            scope = int(lock.get("scope"))
            type = int(lock.get("type"))
            timeout = int(lock.get("timeout"))
            exp = int(lock.get("expires"))
            l = Lock(princ, owner, depth, scope, timeout, locktype=type)
            l.expires = exp
            l.token = uuid.UUID(token)
            self.__locks[token] = l
        for res in doc.iter(tag='res'):
            resid = res.get("resid")
            self.__lockedResources[resid] = []
            for lock in res.iter(tag='reslock'):
                token = lock.get("token")
                self.__lockedResources[resid].append(self.__locks[token])

    def __marshall(self):
        root=ET.Element('lockbase')
        doc=ET.ElementTree(root)

        xlocks=ET.SubElement(root,'locks')
        for tok, lock in self.__locks.iteritems():
            xlock = ET.SubElement(xlocks,'lock')
            xlock.set("token", tok)
            xlock.set("principal", str(lock.principal))
            xlock.set("depth", str(lock.depth))
            xlock.set("scope", str(lock.scope))
            xlock.set("type", str(lock.type))
            xlock.set("timeout", str(lock.timeout))
            xlock.set("expires", str(lock.expires))
            xlockowner=ET.SubElement(xlock,"owner")

            if lock.owner.has_key('uri'):
                xlockowner.set("type", "uri")
                xlockowner.set("uri", lock.owner['uri'])
            else:
                xlockowner.set("type", "text")
                xlockowner.set("text", lock.owner['text'])

        xresources=ET.SubElement(root,'resources')
        for resid, locks in self.__lockedResources.iteritems():
            xres = ET.SubElement(xresources,'res')
            xres.set("resid", resid)
            for lock in locks:
                xlock=ET.SubElement(xres,"reslock")
                xlock.set("token", lock.token.urn[9:])

        return doc


    def __getLockObjects(self, resid):
        """ returns a list of lock for a resource (including locks on parent collections)
        """
        try:
            collectedlocks = self.__lockedResources[resid]
        except KeyError:
            collectedlocks = []
        for res, locks in self.__lockedResources.iteritems():
            if is_prefix(res, resid):
                collectedlocks.extend(locks)
        return collectedlocks


    def __checkTimeout(self):
        """ release all the locks that have expired.
        This method is called by all interface methods in the lock service
        before anything else is done.
        """
        exptk = [l.token for l in self.__locks.values() if  l.expires < int(time())]
        for t in exptk:
            self.__locks.pop(t.urn[9:])
        toremove = []
        for (r, ll) in self.__lockedResources.iteritems():
            nt = [l for l in ll if not l.token in exptk]
            if len(nt):
                self.__lockedResources[r] = nt
            else:
                toremove.append(r)
        for r in toremove:
            self.__lockedResources.pop(r)
        if len(toremove):
            self.__flushlocks()

    def __hackDAVNS(self, msg):
        self.davns = "DAV:d"
        
        msg = re.sub(r"xmlns\s*=\s*(['\"])DAV:['\"]", r"xmlns=\1DAV:d\1", msg)
        msg = re.sub(r"xmlns:([a-zA-Z][a-zA-Z0-9_]*)\s*=\s*(['\"])DAV:['\"]", r"xmlns:\1=\2DAV:d\2", msg)
        return msg

    def __unhackDAVNS(self, msg):
        msg = re.sub(r"^%s$" % self.davns, "DAV:", msg)
        return msg


def is_prefix(uri1,uri2):
    """ returns 1 of uri1 is a prefix of uri2 """
    u1=unicode(uri1).strip('/').split('/')
    u2=unicode(uri2).strip('/').split('/')
    debug("LOCK   IS PREFIX u1 %s" %u1)
    debug("LOCK   IS PREFIX u2 %s" %u2)
    return (len(u1) < len(u2)) and u2[:len(u1)]==u1

def is_parent(uri1,uri2):
    """ returns 1 of uri1 is parent  of uri2 """
    u1=unicode(uri1).strip('/').split('/')
    u2=unicode(uri2).strip('/').split('/')
    debug("LOCK   IS PREFIX u1 %s" %u1)
    debug("LOCK   IS PREFIX u2 %s" %u2)
    return (len(u1) == len(u2)-1) and u2[:len(u1)]==u1

