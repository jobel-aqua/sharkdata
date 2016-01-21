"""
Template for Django settings. Django version 1.6.1.
- Replace all '<REPLACE>' with proper values.
- 'proj_sharkdata' should also be replaced if the 
  django project folder has a different name.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Application specific constants.
APP_DATASETS_FTP_PATH = u'<REPLACE>' 
# APP_DATASETS_FTP_PATH = u'C:/Users/example/Desktop/FTP' # Windows example.
# APP_DATASETS_FTP_PATH = u'/srv/django/proj_sharkdata/' # Unix example.
APPS_VALID_USERS_AND_PASSWORDS_FOR_TEST = {u'<REPLACE>': u'<REPLACE>', u'<REPLACE>': u'<REPLACE>'}


# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '6pz8bnw1nlv9_!lh&*)00%3d9&bk8v5+!4u0o5cpcbe#8gum-8' # Default from Django.
SECRET_KEY = '<REPLACE>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False
# DEBUG = True
# TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #
    'django.contrib.gis', # For Postgresql/PostGIS.
    'app_sharkdata_base',
    'app_datasets',
    'app_resources',
    'app_speciesobs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
###    'django.middleware.csrf.CsrfViewMiddleware', # TODO.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'proj_sharkdata.urls'

WSGI_APPLICATION = 'proj_sharkdata.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # For Postgresql/PostGIS.
        'NAME': 'django_sharkdata',
        'USER': 'postgres',
        'PASSWORD': '<REPLACE>',
        'HOST': 'localhost',
        'PORT': '', # Set to empty string for default.
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files will be collected and put here by running the 
# command: python manage.py collectstatic
STATIC_ROOT = '/srv/django/sharkdata/static/'

STATICFILES_DIRS = (
    '/srv/django/sharkdata/src/app_sharkdata_base/static',
)

STATIC_URL = '/static/'
