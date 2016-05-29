# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from kserver.models import UserProject

from kolekti.synchro import SVNProjectManager

@receiver(post_save, sender=UserProject)
def post_save_userproject_callback(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    logger.debug('post save handler')
    if created:
        username = instance.user.username
        # TODO : use urllib (Win compatibility)
        url  = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, instance.project.directory)
        logger.debug('checkout %s %s'%(username, url))
        projectsroot = os.path.join(settings.KOLEKTI_BASE, username)
        try:
            SVNProjectManager(projectsroot, username = username).checkout_project(instance.project.directory, url)
        except:
            logger.exception('error during checkout')
