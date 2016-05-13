import os
import tempfile
import shutil
import logging
logger = logging.getLogger(__name__)
import urllib2
import pysvn
import locale
import sys

LOCAL_ENCODING=sys.getfilesystemencoding()

from kolekti.exceptions import *


def initLocale():
    # init the locale
    if sys.platform in ['win32','cygwin']:
        locale.setlocale( locale.LC_ALL, '' )

    else:
        language_code, encoding = locale.getdefaultlocale()
        if language_code is None:
            language_code = 'en_GB'

        if encoding is None:
            encoding = 'UTF-8'
        if encoding.lower() == 'utf':
            encoding = 'UTF-8'

        try:
            # setlocale fails when params it does not understand are passed
            locale.setlocale( locale.LC_ALL, '%s.%s' % (language_code, encoding) )
        except locale.Error:
            # force a locale that will work
            locale.setlocale( locale.LC_ALL, 'fr_FR.UTF-8' )
initLocale()


class SvnClient(object):
    statuses_modified = [
        pysvn.wc_status_kind.deleted,
        pysvn.wc_status_kind.added,
        pysvn.wc_status_kind.modified,
        pysvn.wc_status_kind.unversioned,
    ]            

    statuses_absent = [
        pysvn.wc_status_kind.missing,
    ]

    statuses_normal = [
        pysvn.wc_status_kind.none,
        pysvn.wc_status_kind.normal,
    ]
            
    statuses_other = [
        pysvn.wc_status_kind.replaced,
        pysvn.wc_status_kind.merged,
        pysvn.wc_status_kind.conflicted,
        pysvn.wc_status_kind.ignored,
        pysvn.wc_status_kind.obstructed,
        pysvn.wc_status_kind.external,
        pysvn.wc_status_kind.incomplete,
        ]
    
    def __init__(self, username=None, password=None, accept_cert=False):
        self._client = pysvn.Client()
        self.__username = username
        self.__password = password
        self.__accept_cert = accept_cert
        
        def get_login( realm, username, may_save ):
            if self.__username is None:
                raise ExcSyncRequestAuth
            return True, self.__username, self.__password, True
        self._client.callback_get_login = get_login

        self._messages = []
        def callback_log_message(arg):
            self._messages.append(arg)
        self._client.callback_get_log_message = callback_log_message
            
        self._notifications = []
        def callback_notification(arg):
            self._notifications.append(arg)
        self._client.callback_notify = callback_notification
        
        def callback_accept_cert(arg):
            print arg
            if self.__accept_cert:
                return  True, 1, True
            if arg['hostname'] == 'kolekti' and arg['realm'] == 'https://07.kolekti.net:443':
                return  True, 12, True
            raise ExcSyncRequestSSL
            
        self._client.callback_ssl_server_trust_prompt = callback_accept_cert
        
class SynchroManager(SvnClient):
    def __init__(self, base):
        super(SynchroManager, self).__init__()
        self._base = base
        try:
            self._info = self._client.info(base)
        except pysvn.ClientError:
            raise ExcSyncNoSync

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts=urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)

    def geturl(self):
        return self._info.get('repos')

    def history(self):
        return self._client.log(self._base)

    def rev_number(self):
        #headrev = self._client.info(self._base)
        headrev = max([t[1].rev.number for t in self._client.info2(self._base)])
        return {"revision":{"number":headrev}}
    
    def rev_state(self):
        #headrev = self._client.info(self._base)
        headrev = max([t[1].rev.number for t in self._client.info2(self._base)])
        statuses = self.statuses()
        status = "N"
        if len(statuses['error']):
            status = "E"
        if len(statuses['conflict']):
            status = "C"
        if len(statuses['merge']):
            status = "M"
        if len(statuses['commit']):
            status = "*"
        if len(statuses['update']):
            status = "U"
            
        return {"revision":{"number":headrev,"status":status}}

    
    def revision_info(self, revision):
        rev = int(revision)
        rev_summ = self._client.diff_summarize(self._base,
                    pysvn.Revision(pysvn.opt_revision_kind.number,rev),
                    self._base,
                    pysvn.Revision(pysvn.opt_revision_kind.number,rev-1),
                    )
        
        rev_info = None,
        # rev_info = self._client.info2(self._base,
        #                         revision = pysvn.Revision(pysvn.opt_revision_kind.number,rev)
        #                         )
        tmpdir = tempfile.mkdtemp()
        diff_text = self._client.diff(tmpdir,
                               self._base,
                               pysvn.Revision(pysvn.opt_revision_kind.number,rev),
                               self._base,
                               pysvn.Revision(pysvn.opt_revision_kind.number,rev-1),
                               header_encoding="utf-8")

        shutil.rmtree(tmpdir)
        return [dict(item) for item in rev_summ], rev_info, diff_text
        
    def statuses(self, path="", recurse = True):
        res = {'ok': [], 'merge':[], 'conflict':[], 'update':[], 'error':[], 'commit':[],'unversioned':[]}
        statuses = self._client.status(self.__makepath(path),
                                       recurse = recurse,
                                       get_all = True,
                                       update = True)
        for status in statuses:
            path = status.path[len(self._base):]
            item = {"path":path,
                    "basename":os.path.basename(path),
                    "rstatus":str(status.repos_text_status),
                    "wstatus":str(status.text_status),
                    "rpropstatus":str(status.repos_prop_status),
                    "wpropstatus":str(status.prop_status),
                    }

            if status.entry is not None:
                item.update({"kind":str(status.entry.kind),
                             "author":status.entry.commit_author})
            else:
                item.update({"kind":"none"})
            if status.text_status == pysvn.wc_status_kind.ignored:
                pass

            elif status.text_status == pysvn.wc_status_kind.unversioned and status.repos_text_status == pysvn.wc_status_kind.none:
                res['unversioned'].append(item)

            elif status.repos_text_status in self.statuses_modified:
                if status.text_status == pysvn.wc_status_kind.added:
                    res['conflict'].append(item)
                elif status.text_status == pysvn.wc_status_kind.unversioned:
                    res['conflict'].append(item)
                elif status.text_status in self.statuses_modified:
                    if (status.repos_text_status == pysvn.wc_status_kind.deleted) and (status.text_status == pysvn.wc_status_kind.deleted or status.text_status == pysvn.wc_status_kind.unversioned):
                        res['update'].append(item)
                    elif status.repos_text_status == pysvn.wc_status_kind.deleted:
                        res['conflict'].append(item)
                    else:
                        if self.merge_dryrun(status.path):
                            res['merge'].append(item)
                        else:
                            res['conflict'].append(item)
                            
                elif status.text_status in self.statuses_absent:
                    res['update'].append(item)
                    
                elif status.text_status in self.statuses_normal:
                    res['update'].append(item)
                    
                else:
                    res['error'].append(item)
                    
            elif status.repos_text_status in self.statuses_normal:
                if status.text_status in self.statuses_absent:
                    res['update'].append(item)
                elif status.text_status in self.statuses_modified:
                    res['commit'].append(item)
                elif status.text_status in self.statuses_normal:
                    res['ok'].append(item)
                    
                else:
                    res['error'].append(item)
            else:
                res['error'].append(item)
            
            
            if status.prop_status in self.statuses_modified:
                if status.repos_prop_status in self.statuses_modified:
                    res['conflict'].append(item)
                else:
                    res['commit'].append(item)
            else:
                if status.repos_prop_status in self.statuses_modified:
                    res['update'].append(item)
        return res


    def merge_dryrun(self, path):
        notifications = []
        def callback_notification_merge(arg):
            notifications.append(arg)
            

        merge_client = pysvn.Client()
        merge_client.callback_notify = callback_notification_merge
        info = merge_client.info(path)
        rurl = info.get('url')
#        print  'dry run '+str(dict(info))
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)
#        print "merge %s W:%s H:%s %s)"%(rurl, workrev, headrev, path)
        merge_client.merge(path, workrev, path, headrev, path, recurse = False, dry_run=True)
        for notif in notifications:
            if notif.get('content_state',None) == pysvn.wc_notify_state.merged:
                return True
        return False

        
    def merge_dryrun_cmd(self, path):
        #self._client.callback_notify = self.callback_notify_merge
        info = self._client.info(path)
            
        rurl = info.get('url')
        logger.debug('dry run '+rurl)
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)
        
        logger.debug("merge %s W:%s H:%s %s)"%(rurl, workrev, headrev, path))

        import subprocess
        cmd = 'svn merge --dry-run -r BASE:HEAD "%s"'%path 
        exccmd = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=False)
        err=exccmd.stderr.read()
        out=exccmd.stdout.read()
        exccmd.communicate()
        out=out.decode(LOCAL_ENCODING)
        return {
            "conflict":[c[3:] for c in out.splitlines() if c[0:3] == 'C  '],
            "merge":[c[3:] for c in out.splitlines() if c[0:3] == 'G  ']
            }

    def resolved(self, file):
        self._client.resolved(self.__makepath(file))

    def update_all(self):
#        print "update_all"
        update_revision = self._client.update(self._base, recurse = True)
#        print "update revision", update_revision
        return update_revision

    def update(self, files):
        osfiles = []
        for f in files:
            osfiles.append(self.__makepath(f))
        update_revision = self._client.update(osfiles)
        
        return update_revision

    def revert(self, files):
        osfiles = []
        for f in files:
            osfiles.append(self.__makepath(f))
        self._client.revert(osfiles, recurse = True)

    def commit_all(self, log_message):
        commit_revision = self._client.checkin(self._base, log_message, recurse = True)
        return commit_revision 

    def commit(self, files, log_message):
        osfiles = []
        for f in files:
            print type(f)
            osfiles.append(self.__makepath(f))
        commit_revision = self._client.checkin(osfiles, log_message, recurse = True)
        return commit_revision 

    def diff(self, path):
        tmpdir = tempfile.mkdtemp()
        diff = self._client.diff(tmpdir, path)
        shutil.rmtree(tmpdir)
        with open(path) as f:
            workdata = f.read()
        headdata = self._client.cat(path)
        return diff, headdata, workdata  

    def post_save(self, path):
        logger.debug("post save synchro : %s"%path)
        if path[:14]=='/publications/':
            logger.debug("skip")
            return
        if path[:8]=='/drafts/':
            return
        ospath = self.__makepath(path)
        try:
            if self._client.info(ospath) is None:
                logger.debug("add")
                self._client.add(ospath)
        except pysvn.ClientError:
            self.post_save(path.rsplit('/',1)[0])

    def move_resource(self, src, dst):
        ossrc = self.__makepath(src)
        osdst = self.__makepath(dst)
        self._client.move(ossrc, osdst,force=True)
        
    def copy_resource(self, src, dst):
        ossrc = self.__makepath(src)
        osdst = self.__makepath(dst)
        self._client.copy(ossrc, osdst)

    def add_resource(self,path):
        ospath = self.__makepath(path)
        self._client.add(ospath)

    def remove_resource(self,path):
        ospath = self.__makepath(path)
        self._client.remove(ospath,keep_local=True,force=True)

    def delete_resource(self,path):
        ospath = self.__makepath(path)
        self._client.remove(ospath,force=True)

    def propset(self, name, value, path):
        ospath = self.__makepath(path)
        logger.debug("svn proset %s %s %s"%(name,value,path))
        self._client.propset(name, value, ospath)
        
    def propget(self, name, path):
        ospath = self.__makepath(path)
        try:
            props = self._client.propget(name, ospath)
            return props.get(ospath.replace('\\','/').encode('utf8'),None)
        except:
            import traceback
            print traceback.format_exc()
            return None
        
class SVNProjectManager(SvnClient):
    def __init__(self, projectsroot, username=None, password=None):
        self._projectsroot = projectsroot
        super(SVNProjectManager, self).__init__(username, password)
        
    def export_project(self, folder, url="http://beta.kolekti.net/svn/quickstart07"):
        ospath = os.path.join(self._projectsroot, folder)
        self._client.export(url, ospath)
        
    def checkout_project(self, folder, url):
        ospath = os.path.join(self._projectsroot, folder)
        try:
            self._client.checkout(url, ospath)
        except pysvn.ClientError:
            import traceback
            print traceback.format_exc()
            raise ExcSyncNoSync
