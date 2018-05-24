import os

DEBUG = True
SITE_ID = 1

TEST_ROOT = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_ROOT = os.path.join(TEST_ROOT, 'fixtures')

MEDIA_ROOT = os.path.join(os.path.dirname(TEST_ROOT), 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(os.path.dirname(TEST_ROOT), 'static')
STATIC_URL = '/static/'

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_ROOT, 'db.sqlite3'),
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    
    'django_extensions',
    'modeltranslation_rosetta',
    'modeltranslation',
    'tests',

    'django.contrib.admin',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth'
            ],
        }
    },
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('ru', gettext('German')),
)

# This is only needed for the 1.4.X test environment
USE_TZ = True

SECRET_KEY = 'easy'
ROOT_URLCONF = 'tests.urls'
