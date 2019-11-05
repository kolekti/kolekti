import os
from django.core.management.base import BaseCommand, CommandError

from kserver_saas.models import Project, UserProfile, UserProject
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from django.core.exceptions import ObjectDoesNotExist
import logging

class Command(BaseCommand):
    help = 'create a user and a project, affects the project to the user'
        
    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('project', type=str)

    def _create_user(self, username, password):
        User = get_user_model()
        user = User.objects.create_user(username, password=password)
        user.is_superuser=False
        user.is_staff=False
        user.email = username + "@dummy.org"
        user.save()

        email = EmailAddress.objects.create(user = user,
                                    email = username + "dummy.org",
                                    primary = True,
                                    verified = True)
        
        email.save()
        
        return user

    def _create_project(self, user, projectname):
        project = Project(name = projectname,
                          description = "project",
                          directory = projectname,
                          owner = user,
        )
        project.save()
        return project

    
    def handle(self, *args, **options):
        User = get_user_model()
        user = options['user']
        project = options['project']
        password = options['password']
        
        try :
            user = User.objects.get(username=user)
            self.stdout.write("User already exist")
        except User.DoesNotExist:
            user = self._create_user(user, password);

        try:
            project = Project.objects.get(directory = project)
            self.stdout.write("Project already exist")
        except Project.DoesNotExist:            
            project = self._create_project(user, project)

        try:
            userproject = UserProject.objects.get(user = user, project__directory = project)
        except UserProject.DoesNotExist:
            userproject = UserProject(user = user,
                                      project = project,
                                      is_saas = True,
                                      is_admin = True)
            userproject.save()
        self.stdout.write("done.")
