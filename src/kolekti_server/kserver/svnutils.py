# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import sys
import subprocess
import tempfile
import pysvn
import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.conf import settings
from kolekti.synchro import SVNProjectManager


# export project from template into temp dir

# create user tem
class CMDMixin(object):
    LOCAL_ENCODING=sys.getfilesystemencoding()
    def start_cmd(self, cmd):
        try:
            exccmd = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=False)
            err=exccmd.stderr.read()
            out=exccmd.stdout.read()
            exccmd.communicate()
            err=err.decode(self.LOCAL_ENCODING)
            out=out.decode(self.LOCAL_ENCODING)
            logger.debug(cmd)
            logger.debug(out)
            logger.debug(err)
        except:
            import traceback
            logger.debug(traceback.format_exc())
            logger.exception("Erreur lors de l'execution de la commande %(cmd)s"% {'cmd': cmd})

        finally:
            exccmd.stderr.close()
            exccmd.stdout.close()
        return out, err 


class SVNUserManager(CMDMixin):
    def add_user(self, username, password):
        # adds user to svn password file [htpasswd] 
        passfile = settings.KOLEKTI_SVN_PASSFILE
        cmd = ['htpasswd','-b'] 
        if not os.path.exists(passfile):
            cmd.append('-c')
        cmd.extend([passfile, username, password])
        self.start_cmd(cmd)

    
        
class SVNProjectCreator(CMDMixin):
    def create_from_template(self, template_url, project_directory, username):
        repo_path = os.path.join(settings.KOLEKTI_SVN_ROOT,project_directory)
        # export template to temp dir
        tmpd = os.path.join(tempfile.mkdtemp(),project_directory)
        client = pysvn.Client()

        def get_login( realm, username, may_save ):
            return True, settings.KOLEKTI_SVNTPL_USER, settings.KOLEKTI_SVNTPL_PASS, True
        client.callback_get_login = get_login

        def callback_accept_cert(arg):
            if arg['hostname'] == 'kolekti' and arg['realm'] == 'https://07.kolekti.net:443':
                return  True, 12, True
            raise Exception("cert not valid")
        client.callback_ssl_server_trust_prompt = callback_accept_cert
        
        client.export(template_url, tmpd)

        # run svnadmin to create repository
        cmd = ["svnadmin","create",repo_path]
        self.start_cmd(cmd)
        
        client = pysvn.Client()
        client.set_default_username(username)
        client.import_(tmpd,'file://'+repo_path, log_message="initial import")
    