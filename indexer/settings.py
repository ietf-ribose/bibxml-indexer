from pathlib import Path
from os import environ, path


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(environ.get("DEBUG", default=0)) == 1

ALLOWED_HOSTS = [
    environ.get("PRIMARY_HOSTNAME"),
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.app.Config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'indexer.urls'

APPEND_SLASH = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'indexer.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DB_NAME'),
        'USER': environ.get('DB_USER'),
        'PASSWORD': environ.get('DB_SECRET'),
        'HOST': environ.get('DB_HOST'),
        'PORT': int(environ.get('DB_PORT')),
    }
}

# NOTE: This project isn’t intended to be used with Django’s auth,
# hence this setting is empty.
AUTH_PASSWORD_VALIDATORS = []


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'build' / 'static'


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery

CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND')

CELERY_SEND_TASK_SENT_EVENT = True

# TODO: Figure out correct identifier scope for the TRACK_STARTED Celery setting
CELERY_TASK_TRACK_STARTED = True
CELERY_TRACK_STARTED = True

CELERY_WORKER_CONCURRENCY = 1
CELERY_TASK_RESULT_EXPIRES = 604800


# Redis

REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')


# BibXML-specific

API_USER = 'ietf'
"""Username for HTTP Basic auth to access management GUI."""

API_SECRET = environ.get('API_SECRET')
"""Secret used to authenticate API requests and access to management GUI."""

PATH_TO_DATA_DIR = environ.get('PATH_TO_DATA_DIR')
"""Deprecated."""

DATASET_TMP_ROOT = environ.get('DATASET_TMP_ROOT')
"""Where to keep fetched source data and data generated during indexing."""

# TODO: Extract KNOWN_DATASETS from environment
KNOWN_DATASETS = [
    'rfcs',
    'ids',
    'rfcsubseries',
    'misc',
    'w3c',
    '3gpp',
    'ieee',
    'iana',
    'doi',
    'nist',
]
"""A list of known dataset IDs.

For up-to-date list of actually available datasets,
see bibxml-data-* repositories under ietf-ribose GitHub organization.
"""

# TODO: Update DATASET_SOURCE_OVERRIDES setting according to currently available Github repos and their branch names
# TODO: Extract DATASET_SOURCE_OVERRIDES from environment
DATASET_SOURCE_OVERRIDES = {
    'rfcsubseries': {
        'bibxml_data': {
            'repo_branch': 'master',
        },
    },
    # "ecma": {
    #         "bibxml_data": {
    #             "git_remote_url": "git://github.com/ietf-ribose/bibxml-data-ecma.git",
    #             "git_branch": "main",
    #         },
    #         "relaton_data": {
    #             "git_remote_url": "git://github.com/relaton/relaton-data-ecma.git",
    #             "git_branch": "master",
    #         },
    #     },
    # "nist": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-nist.git",
    #         "git_branch": "main",
    #         "local_repo_dir": "relaton-data-nist"
    #     },
    # "ietf": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-ietf.git",
    #         "git_branch": "main",
    #         "local_repo_dir": "relaton-data-ietf"
    #     },
    # "itu-r": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-itu-r.git",
    #         "git_branch": "master",
    #         "local_repo_dir": "relaton-data-itu-r"
    #     },
    # "calconnect": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-calconnect.git",
    #         "git_branch": "main",
    #         "local_repo_dir": "relaton-data-calconnect"
    #     },
    # "cie": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-cie.git",
    #         "git_branch": "master",
    #         "local_repo_dir": "relaton-data-cie"
    #     },
    # "iso": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-iso.git",
    #         "git_branch": "main",
    #         "local_repo_dir": "relaton-data-iso"
    #     },
    # "bipm": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-bipm.git",
    #         "git_branch": "master",
    #         "local_repo_dir": "relaton-data-bipm"
    #     },
    # "iho": {
    #         "git_remote_url": "git://github.com/relaton/relaton-data-iho.git",
    #         "git_branch": "master",
    #         "local_repo_dir": "relaton-data-iho"
    #     },
}
"""Overrides dataset bibxml and/or relaton source. Supports partial override."""
