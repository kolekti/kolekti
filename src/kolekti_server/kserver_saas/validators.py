import os
import subprocess

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

import logging
logger = logging.getLogger('kolekti.'+__name__)
    

class HTPasswordGenerator(object):

    def validate(self, password, user=None):
        return None
    
    def password_changed(self, password, user=None):
        # update htpasswd file for the user
        
        if hasattr(settings, 'AUTH_SYNC_HTPASS'):
            login = user.username
            cmd = ['htpasswd','-b', settings.AUTH_SYNC_HTPASS, user.username,  password]
            
            if not os.path.isfile(settings.AUTH_SYNC_HTPASS):
                cmd.insert(1, '-c')

            logger.debug(" ".join(cmd))
            try:
                exccmd = subprocess.Popen(
                    ' '.join(cmd),
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    close_fds=False)
                err=exccmd.stderr.read()
                out=exccmd.stdout.read()
                exccmd.communicate()
                logger.debug(err)
                logger.debug(out)

            except:
                logger.exception("password change")
                # if subprocess.call(cmd) != 0:
                raise ValidationError(
                    _("The svn password file could not be generated."),
                    code='password_htpasswd_fail',
                    )
                                                                                        

                         
    def get_help_text(self):
        return _(
            "your password will allow you to access svn"
            )
