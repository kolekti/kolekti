# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import os
import stat
import shutil
import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import get_valid_filename

from kserver.models import Project, UserProject

from kolekti.synchro import SVNProjectManager
from kserver.svnutils import SVNProjectCreator

@receiver(post_save, sender=Project)
def post_save_project_callback(sender, **kwargs):
    created = kwargs['created']
    raw = kwargs['raw']
    instance = kwargs['instance']
    logger.debug('post save handler: save project')
    
    if created or raw:
        # export the project template
        try:
            pc = SVNProjectCreator()
            pc.create_from_template(instance.template.svn, instance.directory, instance.owner.username, instance.template.svn_user, instance.template.svn_pass)
        except:
            logger.exception('could not create project from template')


@receiver(post_delete, sender = Project)
def post_delete_project_callback(sender, **kwargs):
    instance = kwargs['instance']
    project_directory = instance.directory
    shutil.rmtree(os.path.join(settings.KOLEKTI_SVN_ROOT, project_directory))
            
@receiver(post_save, sender=UserProject)
def post_save_userproject_callback(sender, **kwargs):
    created = kwargs['created']
    raw = kwargs['raw']
    instance = kwargs['instance']
    logger.debug('post save handler: save userproject')
    if created or raw:
        username = instance.user.username
        # TODO : use urllib (Win compatibility)
        project_directory = instance.project.directory

        url  = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, project_directory)
        logger.debug('checkout %s %s'%(username, url))
        projectsroot = os.path.join(settings.KOLEKTI_BASE, username)
        try:
            SVNProjectManager(projectsroot, username = username).checkout_project(project_directory, url)
        except:
            logger.exception('error during checkout')
        __generate_hooks(instance.project)

@receiver(post_delete, sender = UserProject)
def post_delete_userproject_callback(sender, **kwargs):
    instance = kwargs['instance']
    project_directory = instance.project.directory
    username = instance.user.username
    shutil.rmtree(os.path.join(settings.KOLEKTI_BASE, username, project_directory))
    __generate_hooks(instance.project)

def __generate_hooks(project):
    hooksfile = os.path.join(settings.KOLEKTI_SVN_ROOT, project.directory, "hooks", "post-commit")
    with open(hooksfile, 'w') as hooks:
        hooks.write("#!/bin/bash\n")
        for user_project in UserProject.objects.filter(project = project):
            username = user_project.user.username
            cmd = "/usr/bin/svn update %s\n"%(os.path.join(settings.KOLEKTI_BASE, username, project.directory))
            hooks.write(cmd)
    st = os.stat(hooksfile)
    os.chmod(hooksfile, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    
