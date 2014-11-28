import tempfile
import logging
import pysvn
from common import  LOCAL_ENCODING


def get_log_message():
    return True, "no message specified"

class synchro(object):
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
        self._info = self._client.info(base)

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
        print "callback merge"
        print args
        
    def merge_dryrun(self, path):
        #self._client.callback_notify = self.callback_notify_merge
        info = self._client.info(path)
#        for k,v in info.iteritems():
#            print k,":",v
            
        rurl = info.get('url')
        print rurl
        workrev = info.commit_revision
        headrev = pysvn.Revision(pysvn.opt_revision_kind.head)
        
        print "merge", rurl, workrev, rurl, headrev, path
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




        
    def foo(self):

        list_remote = self._client.list(self._info.url, recurse = True)
        logging.debug('--- remote')
        for remote_status in list_remote:
            local_path = self._base + f[0].repos_path[1:]
            
            #logging.debug(path)
            remote_rev = remote_status[0].created_rev.number
            #logging.debug('remote rev '+str(remote_rev))
            try:
                if os.path.exists(local_path):
                    local_status = self._client.status(local_path)[0]
                    #logging.debug("local rev " + str(local_status.is_versioned))
                    #logging.debug("local rev " + str(local_status.text_status))
                    if local_status.entry is None:
                        stats.update({path:{"local":local_status,
                                            "remote":remote_status[0]}})
                        logging.debug(path + " not present in local")
                    
                    else:
                        local_rev = local_status.entry.revision.number
                        if remote_rev > local_rev:
                            logging.debug(path + " outdated")
                            if local_status.text_status != pysvn.wc_status_kind.normal:
                                stats.update({path:{"local":local_status,
                                                    "remote":remote_status[0]}})

                                logging.debug(" +--> local status modified "+str(local_status.text_status))
            except IndexError:
                logging.debug(path + " local not found ")


        logging.debug('---')
        
        changes = self._client.status(self._base, update=True)
        #print changes
        return {
            "added" :     [f.path for f in changes if f.text_status == pysvn.wc_status_kind.added],
            "removed":    [f.path for f in changes if f.text_status == pysvn.wc_status_kind.deleted],
            "changed":    [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified],
            "conflict":  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.conflicted],
            "unversioned":[f.path for f in changes if f.text_status == pysvn.wc_status_kind.unversioned],
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
