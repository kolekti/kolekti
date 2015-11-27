from django.db import models

class Settings(models.Model):
    active_project = models.CharField(max_length=30)
    active_srclang = models.CharField(max_length=5)
    active_publang = models.CharField(max_length=5)

class ReleaseFocus(models.Model):
    release = models.CharField(max_length = 254)
    assembly = models.CharField(max_length = 30)
    lang = models.CharField(max_length=5)
    state = models.BooleanField(default = False)
