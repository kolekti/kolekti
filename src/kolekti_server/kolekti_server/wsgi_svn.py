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

def check_password(environ, user, password):
  svn_root = "/svn" #TODO: kolekti_server app has this setting
  repo_name = environ.get("PATH_INFO").split("/")[len(svn_root.split("/"))]
  return False
