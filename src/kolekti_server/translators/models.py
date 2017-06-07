import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from kserver_saas.models import Project

import logging
logger = logging.getLogger('kolekti.'+__name__)

from kolekti.synchro import SVNProjectManager

# Create your models here.

# class TranslatorProject

class TranslatorReleaseManager(models.Manager):
    def create(self, project, user, release_name):
        logger.debug('create translator release')
        translator_release = super(TranslatorReleaseManager, self).create(project = project, user = user, release_name = release_name)
        user_project_directory = os.path.join(settings.KOLEKTI_BASE, user.username, project.directory)
        url = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, project.directory)    
        # do something with the book
        if not os.path.exists(user_project_directory):
            logger.debug('checkout : %s', url)
            projectsroot = os.path.join(settings.KOLEKTI_BASE, user.username)
            SVNProjectManager(projectsroot, username = user.username).checkout_project(project.directory, url)
        else:
            pass
        return translator_release
        
class TranslatorRelease(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    release_name = models.CharField(max_length = 255)

    objects = TranslatorReleaseManager()
                                
