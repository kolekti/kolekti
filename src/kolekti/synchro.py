import os
import tempfile
import logging
import urllib2
import pysvn
#from common import  LOCAL_ENCODING
import sys
LOCAL_ENCODING=sys.getfilesystemencoding()

from exceptions import ExcSyncNoSync

def get_log_message(arg):
    pass

class SynchroManager(object):
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
    
    def __init__(self, base):
        self._base = base
        self._client = pysvn.Client()
        self._client.callback_get_log_message = get_log_message
        try:
            self._info = self._client.info(base)
        except pysvn.ClientError:
            raise ExcSyncNoSync

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts = urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)

    def geturl(self):
        return self._info.get('repos')

    def history(self):
        return self._client.log(self._base)
        
    def statuses(self):
        res = {'ok': [], 'merge':[], 'update':[], 'error':[], 'commit':[]}
        statuses = self._client.status(self._base, recurse = True, get_all = True, update = True)
        for status in statuses:
            item = {"path":status.path,
                    "rstatus":status.repos_text_status,
                    "wstatus":status.text_status,
                    }
            if status.entry is not None:
                item.update({"kind":str(status.entry.kind)})
            else:
                item.update({"kind":"none"})
            if status.text_status == pysvn.wc_status_kind.ignored:
                pass
            elif status.text_status == pysvn.wc_status_kind.unversioned and status.repos_text_status == pysvn.wc_status_kind.none:
                pass
            elif status.repos_text_status in self.statuses_modified:
                if status.text_status in self.statuses_modified:
                    res['merge'].append(item)
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


        return res

    def callback_notify_merge(self, args):
        logging.debug("callback merge")
        logging.debug(str(args))
        
    def merge_dryrun(self, path):
        #self._client.callback_notify = self.callback_notify_merge
        info = self._client.info(path)
            
        rurl = info.get('url')
        logging.debug('dry run '+rurl)
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)
        
        logging.debug("merge %s W:%s H:%s %s)"%(rurl, workrev, headrev, path))
        #self._client.merge(rurl, workrev, rurl, headrev, path, dry_run=True)
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

    def update_all(self):
        update_revision = self._client.update(self._base, recurse = True)
        return update_revision

    def commit_all(self, log_message):
        commit_revision = self._client.checkin(self._base, log_message, recurse = True)
        return commit_revision 

    def diff(self, path):
        tmpdir = tempfile.mkdtemp()
        diff = self._client.diff(tmpdir, path)
        with open(path) as f:
            workdata = f.read()
        headdata = self._client.cat(path)
        return diff, headdata, workdata  

    def post_save(self, path):
        logging.debug("post save synchro : %s"%path)
        if path[:14]=='/publications/':
            logging.debug("skip")
            return
        if path[:8]=='/drafts/':
            return
        ospath = self.__makepath(path)
        try:
            if self._client.info(ospath) is None:
                logging.debug("add")
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

    def delete_resource(self,path):
        ospath = self.__makepath(path)
        self._client.remove(ospath,force=True)

class SVNProjectManager(object):
    def __init__(self, projectsroot):
        self._projectsroot = projectsroot
        self._client = pysvn.Client()
        self._client.callback_get_log_message = get_log_message

    def export_project(self, folder, url="http://beta.kolekti.net/svn/quickstart07"):
        ospath = os.path.join(self._projectsroot, folder)
        self._client.export(url, ospath)

    def checkout_project(self, folder, url):
        ospath = os.path.join(self._projectsroot, folder)
        self._client.checkout(url, ospath)
