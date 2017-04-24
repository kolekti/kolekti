from django.db import models
from django.contrib.auth.models import User
from kserver_saas.models import Project

# Create your models here.

# class TranslatorProject

class TranslatorRelease(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    release_name = models.CharField(max_length = 255)

    
