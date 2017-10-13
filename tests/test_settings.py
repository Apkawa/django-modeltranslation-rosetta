# coding: utf-8
from __future__ import unicode_literals

from .settings import *

MEDIA_ROOT = '/tmp/media/'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
