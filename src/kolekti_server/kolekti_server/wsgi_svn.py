"""
WSGI config for kolekti_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kolekti_server.settings_svn")

application = get_wsgi_application()

from django.contrib.auth.models import User, Group
from kserver.models import UserProject

def check_password(environ, user, password):
    repo_dir = environ.get("PATH_INFO").split("/")[2]
    repo_owner_pk, repo_name = repo_dir.split('_', 1)
    
    repo_owner = User.objects.get(pk = repo_owner_pk)
    # checks that the username is valid
    try:
        user = User.objects.get(username=user, is_active=True)
    except User.DoesNotExist:
        return False

    # verifies that the password is valid for the user
    if not user.check_password(password):
        return False
    
    try:
        
        userproject = UserProject.objects.get(project__directory = repo_name, project__owner = repo_owner)
        return True
    except UserProject.DoesNotExist:
        return False
    
    return False
                                                                                    
