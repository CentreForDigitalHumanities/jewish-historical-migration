"""
Django settings for jewish-historical-migration project.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from .common_settings import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kxreeb3bds$oibo7ex#f3bi5r+d(1x5zljo-#ms=i2%ih-!pvn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'backend', 'testserver']


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('PGDATABASE') or 'jewish_historical_migration',
        'USER': os.environ.get('PGUSER') or 'jewish_historical_migration',
        'PASSWORD': os.environ.get('PGPASSWORD') or 'jewish_historical_migration',
        'HOST': os.environ.get('PGHOST') or 'localhost',
        'PORT': os.environ.get('PGPORT') or '5432',
    }
}
