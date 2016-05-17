from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length = 32)
    description = models.CharField(max_length = 255)

class UserProject(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    is_saas = models.BooleanField(default = False)
    is_admin = models.BooleanField(default = False)
    active = models.BooleanField(default = False)
    src_lang = models.CharField(max_length = 5)
    pub_lang = models.CharField(max_length = 5)
    
    

class Settings(models.Model):
    active_project = models.CharField(max_length = 30)
    active_srclang = models.CharField(max_length=5)
    active_publang = models.CharField(max_length=5)

class ReleaseFocus(models.Model):
    release = models.CharField(max_length = 254)
    assembly = models.CharField(max_length = 30)
    lang = models.CharField(max_length=5)
    state = models.BooleanField(default = False)
