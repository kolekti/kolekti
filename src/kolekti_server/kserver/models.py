from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    name = models.CharField(max_length = 64)
    description = models.TextField()
    svn = models.CharField(max_length = 255)
    

class Project(models.Model):
    name = models.CharField(max_length = 32)
    directory = models.CharField(max_length = 32)
    description = models.CharField(max_length = 255)
    owner = models.ForeignKey(User)
    template = models.ForeignKey(Template)

class userProfile(models.Model):
    user = models.OneToOne(User)
    company = models.CharField(max_length = 255)
    address = models.TextField()
    city = models.CharField(max_length = 255)
    zipcode = models.CharField(max_length = 32)
    phone = models.CharField(max_length = 32)
    activeproject = models.ForeignKey(UserProject, on_delete = models.SET_NULL)
    
class UserProject(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

    is_saas = models.BooleanField(default = False)
    is_admin = models.BooleanField(default = False)

    srclang = models.CharField(max_length = 5)
    publang = models.CharField(max_length = 5)


class Pack(models.Model):
    name  = models.CharField(max_length = 30)
    description  = models.TextField()
    price = models.IntegerField()
    users_saas = models.IntegerField()
    users_svn = models.IntegerField()
    templates = model.ManyToOne(Template)
    
class Order(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    pack = models.ForeignKey(Pack)
    date = models.DateField()
    active = models.BooleanField(default = False)



    
class Settings(models.Model):
    active_project = models.CharField(max_length = 30)
    active_srclang = models.CharField(max_length=5)
    active_publang = models.CharField(max_length=5)

class ReleaseFocus(models.Model):
    release = models.CharField(max_length = 254)
    assembly = models.CharField(max_length = 30)
    lang = models.CharField(max_length=5)
    state = models.BooleanField(default = False)
