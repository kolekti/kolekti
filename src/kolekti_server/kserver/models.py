from django.db import models

class Settings(models.Model):
    active_project = models.CharField(max_length=30)
    active_srclang = models.CharField(max_length=5)
    active_publang = models.CharField(max_length=5)

