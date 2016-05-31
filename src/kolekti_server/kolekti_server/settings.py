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

KOLEKTI_CONFIG = settings()
KOLEKTI_BASE = KOLEKTI_CONFIG.get('InstallSettings').get('projectspath')
KOLEKTI_SVN_ROOT = KOLEKTI_CONFIG.get('InstallSettings').get('svnroot','')
KOLEKTI_SVN_PASSFILE = KOLEKTI_CONFIG.get('InstallSettings').get('svnpassfile','')
KOLEKTI_SVN_GROUPFILE = KOLEKTI_CONFIG.get('InstallSettings').get('svngroupfile','')
KOLEKTI_LANGS = ['fr','en','us','de','it']

KOLEKTI_SVNTPL_USER = KOLEKTI_CONFIG.get('SvnRemotes').get('svnuser','')
KOLEKTI_SVNTPL_PASS = KOLEKTI_CONFIG.get('SvnRemotes').get('svnpass','')


#KOLEKTI_SVN

# APP_DIR  = KOLEKTI_CONFIG.get('InstallSettings').get('installdir')
if os.sys.platform[:3] == "win":
    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
    DB_NAME = appdatadir + '\\db.sqlite3'
    DB_NAME = DB_NAME.replace('\\','/')
else:
    DB_NAME = os.path.join(BASE_DIR, 'db.sqlite3')

try:
    os.makedirs(os.path.join(KOLEKTI_BASE,'.logs'))
except:
    pass


LOG_PATH = os.path.join(KOLEKTI_BASE,'.logs')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '47+&9*yikq4^1_fpxaf32!u^5&m(tw7dssr+h-%4sq&3uzz7q9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = False

HOSTNAME='0.0.0.0'
ALLOWED_HOSTS = ['192.168.1.234','citrouille','127.0.0.1', 'localhost']

# SMTP config

EMAIL_HOST="mail.gandi.net"
EMAIL_PORT=465
EMAIL_HOST_USER="kolekti@kolekti.net"
EMAIL_HOST_PASSWORD="yofUden8"
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL="kolekti@kolekti.net"

# Application definition

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'console': {
            'format': '[%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'debug.log'),
            'formatter':'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'info.log'),
            'formatter':'simple',
        },
        'file_kolekti': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_PATH, 'kolekti.log'),
            'formatter':'verbose',
        },
        'console_kolekti': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter':'console',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.info': {
            'handlers': ['file_info'],
            'level': 'INFO',
            'propagate': True,
        },
        'kolekti': {
            'handlers': ['file_kolekti'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'registration': {
            'handlers': ['file_kolekti'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'bootstrapform',
    'kserver',
    'elocus',
    'ecorse',
#    'kmanager',
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

ACCOUNT_ACTIVATION_DAYS = 7

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases


# APP_DIR  = KOLEKTI_CONFIG.get('InstallSettings').get('installdir')
#if os.sys.platform[:3] == "win":
#    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
#    DB_NAME = appdatadir + '\\db.sqlite3'
#    DB_NAME = DB_NAME.replace('\\','/')
#else:
#    DB_NAME = os.path.join(BASE_DIR, 'db.sqlite3')


    
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_NAME,
#        'ENGINE': 'django.db.backends.mysql',
#        'OPTIONS': {
#            'read_default_file': '/home/waloo/my.cnf',
#        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fr_fr'
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
    "/home/waloo/kolekti/src/kolekti_server/kserver/templates",
)
RE_BROWSER_IGNORE=["~$","^\.svn$", "^#.*#$"]

# kolekti configuration

STATICFILES_DIRS = (
    KOLEKTI_BASE,
)
# settings for active project

