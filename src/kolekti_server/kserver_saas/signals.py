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
from django.contrib.auth.models import Group, User

from allauth.account.signals import user_signed_up
from invitations.signals import invite_accepted

from kserver_saas.models import Project, UserProject, UserProfile

from kolekti.synchro import SVNProjectManager
from kserver_saas.svnutils import SVNProjectCreator, SVNUtils

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
    project_directory = os.path.join(settings.KOLEKTI_SVN_ROOT, instance.directory)
    if os.path.exists(project_directory):
        shutil.rmtree(project_directory)
            
@receiver(post_save, sender=UserProject)
def post_save_userproject_callback(sender, **kwargs):
    created = kwargs['created']
    raw = kwargs['raw']
    instance = kwargs['instance']
    logger.debug('post save handler: save userproject')
    if instance.is_saas:
        if created or raw:
            project_directory = instance.project.directory
            username = instance.user.username
            # TODO : use urllib (Win compatibility)
                
            url  = "file://%s/%s"%(settings.KOLEKTI_SVN_ROOT, project_directory)
            logger.debug('checkout %s %s'%(username, url))
            projectsroot = os.path.join(settings.KOLEKTI_BASE, username)
            user_project_directory = os.path.join(projectsroot, project_directory)            
            if not os.path.exists(user_project_directory):
                try:
                    SVNProjectManager(projectsroot, username = username).checkout_project(project_directory, url)
                    u = SVNUtils()
                    u.generate_hooks(instance.project)
                    u.generate_htgroup()
                except:
                    logger.exception('Could not create user project')
                    if os.path.exists(user_project_directory):
                        shutil.rmtree(user_project_directory)
            
            
@receiver(post_delete, sender = UserProject)
def post_delete_userproject_callback(sender, **kwargs):
    instance = kwargs['instance']
    if instance.is_saas:
        username = instance.user.username
        user_project_directory = os.path.join(settings.KOLEKTI_BASE, username, instance.project.directory)
        if os.path.exists(user_project_directory):
            shutil.rmtree(user_project_directory)
        try:
            u = SVNUtils()
            u.generate_hooks(instance.project)
            u.generate_htgroup()
        except:
            logger.exception('Could not update project repository')

                                                                                                                                           
    
@receiver(user_signed_up)
def post_sign_up_callback(sender, **kwargs):
    logger.debug('signup callback')
    user = kwargs['user']
    
    up = UserProfile(user = user)
    up.save()
    
@receiver(invite_accepted)
def post_invite_callback(sender, **kwargs):
    logger.debug('invite callback')
    email = kwargs['email']
    try:
        user = User.objects.get(email = email)
        group = Group.objects.get(name='translator')
        user.groups.add(group)
        
    except User.DoesNotExist:
        logger.exception('user not found')
