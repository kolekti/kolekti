# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def init_template(apps, schema_editor):
    # create template for projects
    Template = apps.get_model('kserver',"Template")
    templ = Template(name = 'elocus',
                     description = 'elocus default template',
                     svn = "https://07.kolekti.net/svn/eLocus")
    templ.save()

    
def create_admin_user(apps, schema_editor):
#    User = apps.get_model('django.contrib.auth', 'User')
    admin = User(
        username='admin',
        email='admin@kolekti.net',
        password=make_password('monculcdupoulet'),
        is_superuser=True,
        is_staff=True,
        )
    admin.save()
    

def create_demo_user(apps, schema_editor):
#    User = apps.get_model('django.contrib.auth', 'User')
    demo = User(
        username='demo',
        email='demo@kolekti.net',
        password=make_password('moidemo'),
        is_superuser=False,
        is_staff=False,
        )
    demo.save()
    UserProfile = apps.get_model('kserver',"UserProfile")
    profile = UserProfile(user = demo)
    profile.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('kserver','0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_template),
        migrations.RunPython(create_admin_user),
#        migrations.RunPython(create_demo_user),
        
    ]
