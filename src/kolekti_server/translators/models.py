import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from kserver_saas.models import Project

import logging
logger = logging.getLogger('kolekti.'+__name__)

from kolekti.synchro import SVNProjectManager
from kolekti.publish import ReleasePublisher
from kolekti.translation import  TranslatorSynchro

# Create your models here.

# class TranslatorProject

class TranslatorReleaseManager(models.Manager):
    def create(self, project, user, release_name):
        sync_mgr = TranslatorSynchro(settings.KOLEKTI_BASE, user.username, project.directory, release_name)
        translator_release = super(TranslatorReleaseManager, self).create(project = project, user = user, release_name = release_name)
        user_release_directory = os.path.join(settings.KOLEKTI_BASE, user.username, project.directory, 'releases', release_name)
        url = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, project.directory)    
        if not os.path.exists(user_release_directory):
            projectsroot = os.path.join(settings.KOLEKTI_BASE, user.username)
            SVNProjectManager(projectsroot, username = user.username).checkout_release(project.directory, url, release_name)
        else:
            sync_mgr._client.update(user_release_directory)
        
        for lang in os.listdir(os.path.join(user_release_directory, 'sources')):
            assemblypath = os.path.join(user_release_directory, 'sources', lang, 'assembly', release_name + '_asm.html')
            if os.path.exists(assemblypath):
                
                state = sync_mgr.lang_state(lang)
                if (not state is None) and (state == 'sourcelang'):                
                    # publish source lang documents
                    release_path = '/releases/'+release_name
                    project_path = os.path.join(settings.KOLEKTI_BASE, user.username, project.directory)
                    try:
                        logger.debug(str((release_name, settings.KOLEKTI_BASE, user, project, lang)))
                        publisher = ReleasePublisher(release_path, settings.KOLEKTI_BASE, user.username, project.directory, langs = [lang])
                        for event in publisher.publish_assembly(release_name + "_asm"):
                            logger.debug(event)
                    except:
                        logger.exception("publication failed")
        
        return translator_release
        
    
class TranslatorRelease(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    release_name = models.CharField(max_length = 255)

    objects = TranslatorReleaseManager()
                                
    def __unicode__(self):
        return u"%s: %s / %s"%(self.user.username,self.project.directory, self.release_name)
