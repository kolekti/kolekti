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
import logging
logger = logging.getLogger('kolekti.'+__name__)
from kolekti.settings import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

KOLEKTI_CONFIG = settings()

def __get_config(env, section, item): 
    try:
        VALUE = os.environ[env]
    except:
        try:
            VALUE = KOLEKTI_CONFIG.get(section).get(item,'')
        except:
            VALUE = ''
    return VALUE

KOLEKTI_BASE = __get_config('KOLEKTI_BASE','InstallSettings','projectspath')
KOLEKTI_SVN_ROOT = __get_config('KOLEKTI_SVN_ROOT','InstallSettings','svnroot')
KOLEKTI_SVN_PASSFILE = __get_config('KOLEKTI_SVN_PASSFILE','InstallSettings','svnpassfile')
KOLEKTI_SVN_GROUPFILE = __get_config('KOLEKTI_SVN_GROUPFILE','InstallSettings','svngroupfile')
KOLEKTI_LANGS = ['fr','en','us','de','it']

KOLEKTI_SVNTPL_USER = __get_config('KOLEKTI_SVNTPL_USER','SvnRemotes','svnuser')
KOLEKTI_SVNTPL_PASS = __get_config('KOLEKTI_SVNTPL_PASS','SvnRemotes','svnpass')


# APP_DIR  = KOLEKTI_CONFIG.get('InstallSettings').get('installdir')
if os.sys.platform[:3] == "win":
    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
    DB_NAME = appdatadir + '\\db.sqlite3'
    DB_NAME = DB_NAME.replace('\\','/')
else:
    DB_NAME = __get_config('KOLEKTI_DBFILE','InstallSettings','database_dir')
    #DB_NAME = os.path.join(DB_DIR, 'db.sqlite3')
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

HOSTNAME=os.getenv('VIRTUAL_HOST','0.0.0.0')
ALLOWED_HOSTS = [HOSTNAME,'127.0.0.1', 'localhost']

# SMTP config

email_config = KOLEKTI_CONFIG.get('smtp_ssl')
if email_config is None:
    email_config = {}

EMAIL_HOST = os.getenv('KOLEKTI_EMAIL_HOST',email_config.get('host',''))
EMAIL_PORT = os.getenv('KOLEKTI_EMAIL_PORT',email_config.get('port',''))
EMAIL_HOST_USER = os.getenv('KOLEKTI_EMAIL_USER',email_config.get('user',''))
EMAIL_HOST_PASSWORD = os.getenv('KOLEKTI_EMAIL_PASSWORD',email_config.get('pass',''))
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL = os.getenv('KOLEKTI_EMAIL_FROM',email_config.get('from',''))

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
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
    'registration',
    'kserver',
    'kserver_saas',
    'django.contrib.admin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'kserver_saas.views.KolektiSaasMiddleware',
)

ROOT_URLCONF = 'kolekti_server.urls'

WSGI_APPLICATION = 'kolekti_server.wsgi.application'

ACCOUNT_ACTIVATION_DAYS = 7

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_NAME,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
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


