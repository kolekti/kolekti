# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    name = models.CharField(max_length = 64)
    description = models.TextField()
    svn = models.CharField(max_length = 255)
    svn_user = models.CharField(max_length = 255, default = "")
    svn_pass = models.CharField(max_length = 255, default = "")
    
    def __unicode__(self):
        return self.name

  
class Project(models.Model):
    name = models.CharField(max_length = 32)
    directory = models.CharField(max_length = 32)
    description = models.CharField(max_length = 255)
    owner = models.ForeignKey(User)
    template = models.ForeignKey(Template)

    def __unicode__(self):
        return u"%s / %s"%(self.owner.username,self.name)
    
    
  
class UserProject(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

    is_saas = models.BooleanField(default = False)
    is_admin = models.BooleanField(default = False)

    srclang = models.CharField(max_length = 5)
    publang = models.CharField(max_length = 5)

    def __unicode__(self):
        return u"%s / %s"%(self.user.username, self.project.name)

    def checkout_project(self):
        username = self.user.username
        svnurl = self.project.directory
        logger.debug('checkout')
        
    def save(self):
        if self.pk is None:
            self.checkout_project()
        return super(UserProject,self).save()
              
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    company = models.CharField(max_length = 255, default = '')
    address = models.TextField(default='', blank=True)
    zipcode = models.CharField(max_length = 32, default='', blank=True)
    city = models.CharField(max_length = 255, default='', blank=True)
    phone = models.CharField(max_length = 32, default='', blank=True)
    created = models.DateField(auto_now_add = True)
    activeproject = models.ForeignKey(UserProject, null = True, default=None, blank=True, on_delete = models.SET_NULL)
    
    def __unicode__(self):
      return self.user.username

class ShareLink(models.Model):
    project = models.ForeignKey(UserProject)
    reportname = models.CharField(max_length = 255)
    hashid = models.CharField(max_length = 255)
    def __unicode__(self):
      return u"%s [%s]"%(self.reportname, self.project)

class Pack(models.Model):
    name  = models.CharField(max_length = 30)
    description  = models.TextField()
    price = models.IntegerField()
    users_saas = models.IntegerField()
    users_svn = models.IntegerField()
    templates = models.ManyToManyField(Template)

    def __unicode__(self):
        return self.name
    
class Order(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    pack = models.ForeignKey(Pack)
    date = models.DateField()
    active = models.BooleanField(default = False)

    def __unicode__(self):
        return self.user + unicode(self.date)


class ReleaseFocus(models.Model):
    release = models.CharField(max_length = 254)
    assembly = models.CharField(max_length = 30)
    lang = models.CharField(max_length=5)
    state = models.BooleanField(default = False)
