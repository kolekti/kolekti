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


import os
import sys
import pysvn
import hashlib

from kolekti.kolekticonf import conf
from kolekti.utils.ioabstraction.FsIO import FsIO
from kolekti.utils.i18n.i18n import tr
from kolekti.logger import debug, dbgexc

__author__ = "Stéphane Bonhomme"
__date__ = "$Jan 27, 2011 12:02:13 AM$"


LOCAL_ENCODING=sys.getfilesystemencoding()
import locale

loc = locale.getdefaultlocale()
if loc == (None, None):
    locale.setlocale(locale.LC_ALL,"fr_FR.UTF8")
else:
    locale.setlocale(locale.LC_ALL,loc)

class svnIO(FsIO):
    __delayed = False

    def __init__(self,http):
        super(svnIO,self).__init__(http)
        self._client=pysvn.Client()
        #self.__status = self._client.info(self.basedir)
        self.__http=http
        
    def _id2local_unicode(self,id):
        l=self._id2local(id)
        return l.decode(LOCAL_ENCODING)

    def _update_repo(self):
        self._client.update(self._basedir)

    def etag(self, id):
        if self.isDir(id):
            token="collection:"+id+":".join(self.getDir(id))
            m=hashlib.md5()
            m.update(token.encode('utf-8'))
        else:
            path=self._id2local_unicode(id)
            l = self._client.log(path,limit=1)[0].get('revision').number
            m=hashlib.md5()
            m.update(str(l))
        return m.hexdigest()

    def mkDir(self, id, logmessage=''):
        path=self._id2local_unicode(id)
        super(svnIO,self).mkDir(id)
        self._client.add(path)
        if not self.__delayed:
            self._client.checkin([path],self._logmsg(logmessage))
            self._update_repo()

    def remove(self, id, logmessage=''):
        try:
            path=self._id2local_unicode(id)
            self._client.remove(path)
            if not self.__delayed:
                self._client.checkin([path],self._logmsg(logmessage) )
        except pysvn.ClientError:
            super(svnIO,self).remove(id)
        if not self.__delayed:
            self._update_repo()

    def rmdir(self, id, logmessage=''):
        path=self._id2local_unicode(id)
        self._client.update(os.path.dirname(path))
        self._client.remove(path)
        if not self.__delayed:
            self._client.checkin([path],self._logmsg(logmessage) )
            self._update_repo()

    def getFile(self, id, rev=None):
        if rev is None:
            return super(svnIO,self).getFile(id)
        else:
            path=self._id2local_unicode(id)
            return self._client.cat(path,revision=pysvn.Revision(pysvn.opt_revision_kind.number, int(rev)))

    def putFile(self, id, data, logmessage=''):
        scheduleadd=False
        path=self._id2local_unicode(id)
        if not self.exists(id):
            scheduleadd=True
        else:
            self._client.update(path)
        super(svnIO,self).putFile(id,data)
        if scheduleadd:
            self._addsvndirs(id)
            self._client.add(path)
        if not self.__delayed:
            self._client.checkin([path],self._logmsg(logmessage))
            self._update_repo()

    def move(self, id, newid,logmessage=''):
        src=self._id2local_unicode(id)
        dst=self._id2local_unicode(newid)
        self._client.update(src)
        self._client.move(src,dst)
        if not self.__delayed:
            self._client.checkin([src,dst],self._logmsg(logmessage) )
            self._update_repo()

    def copyDirs(self, id, destid,logmessage=''):
        src=self._id2local_unicode(id)
        dst=self._id2local_unicode(destid)
        super(svnIO,self).copyDirs( id, destid)
        self._client.remove(src)
        self._client.add(dst)
        if not self.__delayed:
            self._client.checkin([src,dst],self._logmsg(logmessage) )
            self._update_repo()

    def makedirs(self, id):
        try:
            super(svnIO,self).makedirs(id)
            self._addsvndirs(id)
        except OSError:
            pass

    def _addsvndirs(self, id):
        if self.isFile(id):
            splitId = id.split('/')[:-1]
        else:
            splitId = id.split('/')
        path=self._id2local_unicode(id)
        p=path[:len(self._basedir)]
        for direc in splitId:
            p = os.path.join(p, direc)
            try:
                self._client.add(p)
                s = tr(u"[0031]Création du dossier")
                if not self.__delayed:
                    self._client.checkin([p],self._logmsg(s.i18n(self.http.translation)))
            except:
                pass

    def svnlog(self,id,limit=0):
        path=self._id2local_unicode(id)
        logs=[]
        try:
            for l in self._client.log(path,limit=limit):
                log={
                    'date':l.get('date'),
                    'author':l.get('author').decode('utf-8'),
                    'number':l.get('revision').number,
                    }
                uid = -1
                msg = l.get('message','').decode('utf-8')
                if msg[:2]=='@@':
                    uid = msg[2:].split(':',1)[0]
                    msg = msg[2:].split(':',1)[1]

                msg = msg.strip()
                log.update({'uid':uid,'msg':msg})
                logs.append(log)
        except pysvn.ClientError:
            pass
        return logs

    def history(self,id,filterfct=(lambda x:True), limit=0):
        path=self._id2local_unicode(id)
        histo=sorted([(i.last_changed_rev.number,i.URL,f) for (f,i) in self._client.info2(path) if filterfct(f)])
        histo=histo[-limit:]
        histo.reverse()
        history=[]
        try:
            for item in histo :
                l=self._client.log(item[1],limit=1)[0]
                log={
                    'path':item[2].decode('utf-8'),
                    'date':l.get('date'),
                    'author':l.get('author').decode('utf-8'),
                    'number':l.get('revision').number,
                    }
                uid = -1
                msg = l.get('message','').decode('utf-8')
                if msg[:2]=='@@':
                    uid = msg[2:].split(':',1)[0]
                    msg = msg[2:].split(':',1)[1]

                msg = msg.strip()
                log.update({'uid':uid,'msg':msg})
                history.append(log)
        except pysvn.ClientError:
            dbgexc()
            pass
        return history

    def _logmsg(self, msg):
        uid=self.__http.getdata('auth','uid')
        if uid is None:
            return msg.encode('utf-8')
        return '@@%s:%s'%(uid,msg.encode('utf-8'))

    def getCreationDate(self, id):
        #returns the creation date of the file as a timestamp
        path=self._id2local_unicode(id)
        l=self._client.log(path)[-1]
        return l.date

    def prop_set(self, id, name, value, rev=None):
        path=self._id2local_unicode(id)
        if rev is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.working)
        else:
            revision = pysvn.Revision(pysvn.opt_revision_kind.number, int(rev))
        self._client.propset(name, value, path, revision=revision)
        if not self.__delayed:
            self._client.checkin([path],self._logmsg(u"Set property %s" %name))

    def prop_get(self, id, name, rev=None):
        path=self._id2local_unicode(id)
        if rev is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.working)
        else:
            revision = pysvn.Revision(pysvn.opt_revision_kind.number, int(rev))
        return self._client.propget(name, path, revision=revision)

    def prop_del(self, id, name, rev=None):
        path=self._id2local_unicode(id)
        if rev is None:
            revision = pysvn.Revision(pysvn.opt_revision_kind.working)
        else:
            revision = pysvn.Revision(pysvn.opt_revision_kind.number, int(rev))
        self._client.propdel(name, path, revision=revision)
        if not self.__delayed:
            self._client.checkin([path],self._logmsg(u"Delete property %s" %name))

    def set_delayed(self, delayed=False):
        self.__delayed = delayed

    def delayed_commit(self, path, logmessage=''):
        self._client.checkin([path],self._logmsg(logmessage))
        self._update_repo()
