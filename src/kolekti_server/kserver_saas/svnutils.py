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


# export project from template into temp dir

# create user tem
class CMDMixin(object):
    """ provides command-lmine utility"""
    LOCAL_ENCODING=sys.getfilesystemencoding()
    def start_cmd(self, cmd):
        logger.debug(cmd)
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
            logger.debug(out)
            logger.debug(err)
            exccmd.stderr.close()
            exccmd.stdout.close()

        except:
            import traceback
            logger.debug(traceback.format_exc())
            logger.exception("Erreur lors de l'execution de la commande %(cmd)s"% {'cmd': cmd})
            out = err = None
            
        return out, err 


class SVNUserManager(CMDMixin):
    """ Class for svn user managing function
        Obsolated with svn_ayuth wsgi script which directly use django auth
        Adds a user to htpasswd file
        """
    def add_user(self, username, password):
        # adds user to svn password file [htpasswd] 
        passfile = settings.KOLEKTI_SVN_PASSFILE
        cmd = ['htpasswd','-b'] 
        if not os.path.exists(passfile):
            cmd.append('-c')
        cmd.extend([passfile, username, password])
        self.start_cmd(cmd)

    
        
class SVNProjectCreator(CMDMixin):
    """ Utilisty to manage projects in local svn repo
    """
    def create_from_template(self, template_url, project_directory, username, svn_user = settings.KOLEKTI_SVNTPL_USER, svn_pass = settings.KOLEKTI_SVNTPL_PASS):
        """ Creates a new project in local repository. Init the new project repo with template export from svn url
        """
        logger.debug("create repo from template")
        repo_path = os.path.join(settings.KOLEKTI_SVN_ROOT,project_directory)
        # export template to temp dir
        tmpd = os.path.join(tempfile.mkdtemp(),project_directory)
        client = pysvn.Client()

        def get_login( realm, username, may_save ):
            logger.debug("login callback")
            return True, svn_user, svn_pass, False
        client.callback_get_login = get_login

        def callback_accept_cert(arg):
            if arg['hostname'] == 'kolekti' and arg['realm'] == 'https://07.kolekti.net:443':
                return  True, 12, False
            raise Exception("cert not valid")
        client.callback_ssl_server_trust_prompt = callback_accept_cert
        
        client.export(template_url, tmpd)

        # run svnadmin to create repository
        cmd = ["svnadmin","create",repo_path]
        self.start_cmd(cmd)
        
        client = pysvn.Client()
        client.set_default_username(username)
        client.import_(tmpd,'file://'+repo_path, log_message="initial import")

        # create hooks environement
        hooksenvfile = os.path.join(settings.KOLEKTI_SVN_ROOT, project_directory, "conf", "hooks-env")
        with open(hooksenvfile, 'w') as f:
            f.write("[default]\n")
            f.write("LANG = C.UTF-8")
            
    
