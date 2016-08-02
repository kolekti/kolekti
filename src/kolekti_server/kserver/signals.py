# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import get_valid_filename

from kserver.models import Project, UserProject

from kolekti.synchro import SVNProjectManager
from kserver.svnutils import SVNProjectCreator

@receiver(post_save, sender=Project)
def post_save_project_callback(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    logger.debug('post save handler: projects')
    if created:
        # export the project template
        project_directory = "%05d_%s"%(instance.owner.pk, get_valid_filename(instance.name))
        pc = SVNProjectCreator()
        pc.create_from_template(instance.template.svn, project_directory, instance.owner.username)


@receiver(post_save, sender=UserProject)
def post_save_userproject_callback(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    logger.debug('post save handler')
    if created:
        username = instance.user.username
        # TODO : use urllib (Win compatibility)
        project_directory = "%05d_%s"%(instance.project.owner.pk, instance.project.directory)

        url  = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, project_directory)
        logger.debug('checkout %s %s'%(username, url))
        projectsroot = os.path.join(settings.KOLEKTI_BASE, username)
        try:
            SVNProjectManager(projectsroot, username = username).checkout_project(project_directory, url)
        except:
            logger.exception('error during checkout')

