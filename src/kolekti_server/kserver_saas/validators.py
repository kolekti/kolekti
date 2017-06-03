from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class HTPasswordGenerator(object):
            
        def validate(self, password, user=None):
            # update htpasswd file for the user
            auth = {}
            if hasattr(settings, 'AUTH_SYNC_HTPASS'):
                with open(setting['AUTH_SYNC_HTPASS'], 'r') as f:
                    for line in f.readlines():
                        user,hashp = line.strip.split(';')
                        auth.update({user:hashp})
                auth.update({user:self._hash(password)})
                with open(setting['AUTH_SYNC_HTPASS'], 'w') as f:
                    for user, hashp in auth.iteritems():
                        f.write('%s:%s'%(user, pass))
                        

                         
        def get_help_text(self):
                return _(
                        "htpasswd generator"
                        )
