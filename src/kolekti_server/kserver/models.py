from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    name = models.CharField(max_length = 64)
    description = models.TextField()
    svn = models.CharField(max_length = 255)
    
    def __unicode__(self):
        return self.name

  
class Project(models.Model):
    name = models.CharField(max_length = 32)
    directory = models.CharField(max_length = 32)
    description = models.CharField(max_length = 255)
    owner = models.ForeignKey(User)
    template = models.ForeignKey(Template)

    def __unicode__(self):
      return u"%s/%s"%(self.name, self.owner.username)
          

class UserProject(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)

    is_saas = models.BooleanField(default = False)
    is_admin = models.BooleanField(default = False)

    srclang = models.CharField(max_length = 5)
    publang = models.CharField(max_length = 5)

    def __unicode__(self):
      return u"%s/%s"%(self.user.username, self.project.name)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    company = models.CharField(max_length = 255, default = '')
    address = models.TextField()
    city = models.CharField(max_length = 255)
    zipcode = models.CharField(max_length = 32)
    phone = models.CharField(max_length = 32)
    created = models.DateField(auto_now_add = True)
    activeproject = models.ForeignKey(UserProject, null = True, on_delete = models.SET_NULL)
    
    def __unicode__(self):
      return self.user.username

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
