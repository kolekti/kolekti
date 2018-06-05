# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

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
            locale.setlocale( locale.LC_ALL, 'C.UTF-8' )
initLocale()


class StatusTree(dict):
    def add_path_item(self, path, item):
        node = self
        for pathstep in path.split('/'):
            if not node.has_key(pathstep):
                node.update({pathstep:{}})
            node = node[pathstep]
        node.update({'__self':item})

    def display(self, node = None, depth = 0):        
        if node is None:
            node = self
        try:
            c = ('-'*depth) + node['__self']['path'].split('/')[-1]
            nbs = 100 - len(c)
            logger.debug(c + (' '*nbs) + node['__self']['kolekti_status'])
        except:
            logger.exception("display")
            pass
        for child in node.keys():
            if child == '__self':
                continue
            self.display(node = node[child], depth = depth + 1)

    def update_statuses(self, node = None):
        if node is None:
            node = self
        if len(node.keys()) == 1 and '__self' in node.keys() :
            children_statuses = []
        else:
            children_statuses = [self.update_statuses(node = node[child]) for child in node.keys() if not child=='__self']
        status = self._update_node_status(node, children_statuses)
        try:
            node['__self'].update({'kolekti_status':status})
        except KeyError:
            pass
        return status

    def _update_node_status(self, node, children_statuses = []):
        kolekti_status = None
        try:
            wstatus = node['__self']['wstatus']
            rstatus = node['__self']['rstatus']
            wpropstatus = node['__self']['wpropstatus']
            rpropstatus = node['__self']['rpropstatus']
            node['__self'].update ({
                "wstatus" : str(wstatus),
                "rstatus" : str(rstatus),
                "wpropstatus" : str(wpropstatus),
                "rpropstatus" : str(rpropstatus),
                })
        except KeyError:
            return ''

        if rstatus in statuses_modified:
            if wstatus == pysvn.wc_status_kind.added:
                kolekti_status='conflict'                
            elif wstatus == pysvn.wc_status_kind.unversioned:
                kolekti_status='conflict'
            elif wstatus in statuses_modified:
                if (rstatus == pysvn.wc_status_kind.deleted) and (wstatus == pysvn.wc_status_kind.deleted or wstatus == pysvn.wc_status_kind.unversioned):
                    kolekti_status='update'
                elif rstatus == pysvn.wc_status_kind.deleted:
                    kolekti_status='conflict'
                else:
                    if self.merge_dryrun(status.path):
                        kolekti_status='merge'
                    else:
                        kolekti_status='conflict'
                            
            elif wstatus in statuses_absent:
                kolekti_status='update'
                    
            elif wstatus in statuses_normal:
                kolekti_status='update'
                    
            else:
                kolekti_status='error'
                    
        elif rstatus in statuses_normal:
            if wstatus in statuses_absent:
                kolekti_status='update'
            elif wstatus in statuses_modified:
                kolekti_status = 'commit'
            elif wstatus in statuses_normal:
                kolekti_status = 'ok'
                    
            else:
                kolekti_status='error'
        else:
            kolekti_status='error'
            
        # properties
        
        if wpropstatus in statuses_modified:
            if rpropstatus in statuses_modified:
                kolekti_status='conflict'
            else:
                kolekti_status = 'commit'
        else:
            if rpropstatus in statuses_modified:
                kolekti_status='update'

        if 'conflict' in children_statuses:
            kolekti_status = "conflict"
        elif 'error' in  children_statuses:
            kolekti_status = "error"
        elif 'update' in children_statuses:
            if kolekti_status == 'commit':
                kolekti_status = "conflict"
            else:
                kolekti_status = 'update'
        elif 'commit' in children_statuses:
            if kolekti_status == 'update':
                kolekti_status = "conflict"
            else:
                kolekti_status = 'commit'
                
        return kolekti_status


    def merge_dryrun(self, path):
        notifications = []
        def callback_notification_merge(arg):
            notifications.append(arg)
            

        merge_client = pysvn.Client()
        merge_client.callback_notify = callback_notification_merge
        info = merge_client.info(path)
        rurl = info.get('url')
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)

        merge_client.merge(path, workrev, path, headrev, path, recurse = False, dry_run=True)
        for notif in notifications:
            if notif.get('content_state',None) == pysvn.wc_notify_state.merged:
                return True
        return False

            
class SvnClient(object):
    
    def __init__(self, username=None, password=None, accept_cert=False):
        self._client = pysvn.Client()
        self.__username = username
        self.__password = password
        self.__accept_cert = accept_cert
        if not username is None:
            self._client.set_default_username(username)
        
        def get_login( realm, username, may_save ):
            if self.__username is None or self.__password is None:
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
            logger.debug("callback certificate %s"%arg)
            if self.__accept_cert:
                return  True, 1, True
            if arg['hostname'] == 'kolekti' and arg['realm'] == 'https://07.kolekti.net:443':
                return  True, 12, True
            raise ExcSyncRequestSSL
            
        self._client.callback_ssl_server_trust_prompt = callback_accept_cert

        def callback_conflict_resolver(arg):
            logger.debug(arg)
            conflict_choice = "mine_full"
            save_merged = None
            merge_file = None
            return conflict_choice, merge_file, save_merged
        
        self._client.callback_conflict_resolver = callback_conflict_resolver
        
class SynchroManager(SvnClient):
    def __init__(self, base, username = None):
        super(SynchroManager, self).__init__(username = username)
        self._base = base
        try:
            self._info = self._client.info(base)
        except pysvn.ClientError:
            logger.exception('unable to setup sync client')
            raise ExcSyncNoSync

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts=urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)

    def _localpath(self, ospath):
        lp = ospath.replace(self._base,'')
        return '/'.join(lp.split(os.path.sep))        
    
    def geturl(self):
        return self._info.get('repos')

    def history(self, limit=20):
        return self._client.log(self._base, limit = limit)

    def rev_number(self):
        h = self._client.log(self._base, limit = 1)
        return {"revision":{"number":h[0].revision.number}}
    
    
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
        
        rev_obj = pysvn.Revision( pysvn.opt_revision_kind.number, rev )
        
        info = self._client.log(self._base, revision_start=rev_obj, revision_end=rev_obj)
        
        rev_summ = self._client.diff_summarize(self._base,
                    pysvn.Revision(pysvn.opt_revision_kind.number,rev-1),
                    self._base,
                    pysvn.Revision(pysvn.opt_revision_kind.number,rev),
                    )

        tmpdir = tempfile.mkdtemp()
        try:
            diff_text = self._client.diff(tmpdir,
                                self._base,
                                pysvn.Revision(pysvn.opt_revision_kind.number,rev-1),
                                self._base,
                                pysvn.Revision(pysvn.opt_revision_kind.number,rev),
                                header_encoding="UTF-8")
        except:
            logger.exception('could not calculate diff')
            diff_text = "impossible de calculer les différences" 
        shutil.rmtree(tmpdir)
        return [dict(item) for item in rev_summ], info[0], diff_text

    def revision_diff(self, revision, path):
        ospath = self.__makepath(path)
        tmpdir = tempfile.mkdtemp()
        try:
            diff_text = self._client.diff(tmpdir,
                                ospath,
                                pysvn.Revision(pysvn.opt_revision_kind.number,rev),
                                ospath,
                                pysvn.Revision(pysvn.opt_revision_kind.number,rev-1),
                                header_encoding="utf-8")
        except:
            diff_text = "impossible de calculer les différences" 
        shutil.rmtree(tmpdir)
        return [dict(item) for item in rev_summ], rev_info, diff_text


    def statuses(self, path="", recurse = True):
        res = StatusTree()
        statuses = self._client.status(self.__makepath(path),
                                       recurse = recurse,
                                       get_all = True,
                                       update = True)

        for status in statuses:
            item_path = self._localpath(status.path)
            item = {"path":self._localpath(status.path),
                    "ospath":status.path,
                    "basename":os.path.basename(status.path),
                    "rstatus":status.repos_text_status,
                    "wstatus":status.text_status,
                    "rpropstatus":status.repos_prop_status,
                    "wpropstatus":status.prop_status,
                    }
            if status.entry is not None:
                item.update({"kind":str(status.entry.kind),
                             "author":status.entry.commit_author})
            else:
                item.update({"kind":"none"})
                
            if status.text_status == pysvn.wc_status_kind.ignored:
                continue
            res.add_path_item(item_path[1:], item)
            
        res.update_statuses()
#        logger.debug("display")
#        res.display()
        return res
        
    def statuses2(self, path="", recurse = True):
        res = {'ok': [], 'merge':[], 'conflict':[], 'update':[], 'error':[], 'commit':[],'unversioned':[]}
        statuses = self._client.status(self.__makepath(path),
                                       recurse = recurse,
                                       get_all = True,
                                       update = True)
        for status in statuses:
            item = {"path":self._localpath(status.path),
                    "ospath":status.path,
                    "basename":os.path.basename(status.path),
                    "rstatus":str(status.repos_text_status),
                    "wstatus":str(status.text_status),
                    "rpropstatus":str(status.repos_prop_status),
                    "wpropstatus":str(status.prop_status),
                    }
                
            if '/sources/en/topics/foo' in self._localpath(status.path):
                logger.debug(self._localpath(status.path))
                logger.debug(dict(status))
                
            if status.entry is not None:
                item.update({"kind":str(status.entry.kind),
                             "author":status.entry.commit_author})
            else:
                item.update({"kind":"none"})
                
            if status.text_status == pysvn.wc_status_kind.ignored:
                pass

            elif status.text_status == pysvn.wc_status_kind.unversioned and status.repos_text_status == pysvn.wc_status_kind.none:
                res['unversioned'].append(item)

            elif status.repos_text_status in statuses_modified:
                if status.text_status == pysvn.wc_status_kind.added:
                    res['conflict'].append(item)
                elif status.text_status == pysvn.wc_status_kind.unversioned:
                    res['conflict'].append(item)
                elif status.text_status in statuses_modified:
                    if (status.repos_text_status == pysvn.wc_status_kind.deleted) and (status.text_status == pysvn.wc_status_kind.deleted or status.text_status == pysvn.wc_status_kind.unversioned):
                        res['update'].append(item)
                    elif status.repos_text_status == pysvn.wc_status_kind.deleted:
                        res['conflict'].append(item)
                    else:
                        if self.merge_dryrun(status.path):
                            res['merge'].append(item)
                        else:
                            res['conflict'].append(item)
                            
                elif status.text_status in statuses_absent:
                    res['update'].append(item)
                    
                elif status.text_status in statuses_normal:
                    res['update'].append(item)
                    
                else:
                    res['error'].append(item)
                    
            elif status.repos_text_status in statuses_normal:
                if status.text_status in statuses_absent:
                    res['update'].append(item)
                elif status.text_status in statuses_modified:
                    res['commit'].append(item)
                elif status.text_status in statuses_normal:
                    res['ok'].append(item)
                    
                else:
                    res['error'].append(item)
            else:
                res['error'].append(item)
            
            
            if status.prop_status in statuses_modified:
                if status.repos_prop_status in statuses_modified:
                    res['conflict'].append(item)
                else:
                    res['commit'].append(item)
            else:
                if status.repos_prop_status in statuses_modified:
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
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)

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
        update_revision = self._client.update(self._base, recurse = True)
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
        self._client.revert(sorted(osfiles, key = len), recurse = True)
            
    def commit_all(self, log_message):
        log_message = log_message.replace('\r\n', '\n')
        commit_revision = self._client.checkin(self._base, log_message, recurse = True)
        return commit_revision 

    def commit(self, files, log_message):
        log_message = log_message.replace('\r\n', '\n')
        osfiles = []
        for f in files:
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
        if path[:14]=='/publications/':
            return
        if path[:8]=='/drafts/':
            return
        ospath = self.__makepath(path)
        try:
            if self._client.info(ospath) is None:
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
        self._client.propset(name, value, ospath)
        
    def propget(self, name, path):
        ospath = self.__makepath(path)
        try:
            props = self._client.propget(name, ospath)
            return props.get(ospath.replace('\\','/').encode('utf8'),None)
        except:
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
            logger.exception("checkout of project failed : %s"%url)
            raise ExcSyncNoSync
        
    def checkout_release(self, folder, url, release):
        ospath = os.path.join(self._projectsroot, folder)
        try:
            if not os.path.exists(ospath):
                self._client.checkout(url + '/kolekti', os.path.join(ospath, "kolekti"))
                self._client.checkout(url + '/sources', os.path.join(ospath, "sources"))
            self._client.checkout(url + "/releases/" + release, os.path.join(ospath, "releases", release))
        except pysvn.ClientError:
            logger.exception("checkout of project failed : %s"%url)
            raise ExcSyncNoSync
        
