import os
import urllib2

import logging
logger = logging.getLogger('kolekti.'+__name__)

from kolekti.synchro import SvnClient
from django.conf import settings



class TranslatorSynchro(SvnClient):
    def __init__(self, path, username, project, release):
        super(TranslatorSynchro, self).__init__(username = username)
        self._base = os.path.join(settings.KOLEKTI_BASE, username, project, 'releases', release)
        self._release = release

    def __makepath(self, path):
        # returns os absolute path from relative path
        pathparts=urllib2.url2pathname(path).split(os.path.sep)
        return os.path.join(self._base, *pathparts)
        
    def lang_state(self, lang):
        assembly = '/'.join(['sources', lang, 'assembly', self._release + '_asm.html']) 
        ospath = self.__makepath(assembly)
        try:
            props = self._client.propget('release_state', ospath)
            state = props.get(ospath.replace('\\','/').encode('utf8'), None)
        except:
            logger.exception('could not get assembly state')
            state = None
            
        if state is None:
            logger.debug(os.path.exists(ospath))
            if os.path.exists(ospath):
                state = "local"
        return state

