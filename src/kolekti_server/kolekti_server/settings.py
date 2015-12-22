"""
Django settings for kolekti_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json
from kolekti.settings import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '47+&9*yikq4^1_fpxaf32!u^5&m(tw7dssr+h-%4sq&3uzz7q9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = False

HOSTNAME='0.0.0.0'
ALLOWED_HOSTS = ['192.168.1.234','citrouille','127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kserver',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kolekti_server.urls'

WSGI_APPLICATION = 'kolekti_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

KOLEKTI_CONFIG = settings()
KOLEKTI_BASE = KOLEKTI_CONFIG.get('InstallSettings').get('projectspath')
# APP_DIR  = KOLEKTI_CONFIG.get('InstallSettings').get('installdir')
if os.sys.platform[:3] == "win":
    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
    DB_NAME = appdatadir + '\\db.sqlite3'
    DB_NAME = DB_NAME.replace('\\','/')
    os.environ['XML_CATALOG_FILES']='/'.join([BASE_DIR,'dtd','w3c-dtd-xhtml.xml'])
else:
    DB_NAME = os.path.join(BASE_DIR, 'db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'NAME': DB_NAME,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = KOLEKTI_CONFIG.get('InstallSettings',{'timezone':"Europe/Paris"}).get('timezone')
#TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_URL = '/static/'
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.    
    "kolekti_server/kserver/templates",
)
RE_BROWSER_IGNORE=["~$","^\.svn$", "^#.*#$"]

# kolekti configuration



#KOLEKTI_CONFIG = settings()
#KOLEKTI_BASE = KOLEKTI_CONFIG.get('InstallSettings').get('projectspath')
#print KOLEKTI_CONFIG

STATICFILES_DIRS = (
    KOLEKTI_BASE,
)

KOLEKTI_LANGS = ['fr','en','us','de','it']

# settings for active project

