"""
Template for Django settings. Django version 1.10.

For SHARKdata:
- Copy this file (TEMPLATE_settings.py) to proj_sharkdata/proj_sharkdata/settings.py
- Replace all '<REPLACE>' with proper values.
"""
from __future__ import unicode_literals

import os
import logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5yjri=xzk%^vqkogswj63pa50ri5$t2h)o43vm1_+4883enj!7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = True

ALLOWED_HOSTS = ['<REPLACE>']
# ALLOWED_HOSTS = ['test.sharkdata.se']


LOGGER = logging.getLogger('SHARKdata')
LOGGING_PATH = None
# LOGGING_PATH = '<REPLACE>'


# Application specific constants.
APP_DATASETS_FTP_PATH = '<REPLACE>'
# APP_DATASETS_FTP_PATH = 'C:/Users/example/Desktop/FTP' # Windows example.
# APP_DATASETS_FTP_PATH = '/srv/django/proj_sharkdata/' # Unix example.
APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST = {'<REPLACE>': '<REPLACE>'}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
###    'django.contrib.gis', # For Postgresql/PostGIS.
    'app_sharkdata_base',
    'app_datasets',
    'app_resources',
    'app_exportformats', 
    'app_speciesobs',
    'app_sharkdataadmin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proj_sharkdata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'proj_sharkdata.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
###        'ENGINE': 'django.contrib.gis.db.backends.postgis', # For Postgresql/PostGIS.
        'ENGINE': 'django.db.backends.postgresql', # For Postgresql.
        'NAME': 'django_sharkdata',
        'USER': '<REPLACE>',
        'PASSWORD': '<REPLACE>',
        'HOST': 'localhost',
        'PORT': '', # Set to empty string for default.
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Stockholm'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
# Static files will be collected and put here by running the 
# command: python manage.py collectstatic
STATIC_ROOT = '/srv/django/sharkdata/static/'
STATICFILES_DIRS = (
    '/srv/django/sharkdata/src/app_sharkdata_base/static',
)
STATIC_URL = '/static/'

if LOGGING_PATH:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file_error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGGING_PATH +'sharkdata_errors.log',
                'maxBytes': 1024*1024,
                'backupCount': 5,
            },
        },
        'loggers': {
            '': {
                'handlers': ['file_error'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }
