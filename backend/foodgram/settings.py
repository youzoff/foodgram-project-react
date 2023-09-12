"""
Django settings for foodgram project.
"""
import environ
import os
from pathlib import Path

env = environ.Env(
    DJANGO_TOKEN=(str, 'django'),
    DJANGO_DEBUG=(bool, False),
    POSTGRES_DB=(str, 'django'),
    POSTGRES_USER=(str, 'django'),
    POSTGRES_PASSWORD=(str, 'pass1'),
    DB_HOST=(str, 'db'),
    DB_PORT=(int, 5432)
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '../.env'))

SECRET_KEY = env('DJANGO_TOKEN')

DEBUG = env('DJANGO_DEBUG')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_filters',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',

    'api',
    'core',
    'recipes',
    'users',
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

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT')
    }
}

# Password validation

AUTH_USER_MODEL = 'users.CustomUser'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CSV_PATH = os.path.join(BASE_DIR, 'static/data')
JSON_PATH = os.path.join(BASE_DIR, 'static/data/ingredients.json')

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

}

# Djoser

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.AllowAny']
    },
    'SERIALIZERS': {
        'user_create': 'api.users.serializers.CustomUserCreateSerializer',
        'user': 'api.users.serializers.CustomUserSerializer',
        'current_user': 'api.users.serializers.CustomUserSerializer',
    },
}

# Constants
CHAR_FIELD_MAX_LENGTH = 200
COLOR_MAX_LENGTH = 7
MIN_TIME_VALUE = 1
AMOUNT_MIN_VALUE = 1

TEST_USERS = (
    {
        'username': 'guitarist',
        'email': 'usermail1@ya.ru',
        'firstname': 'Billy',
        'lastname': 'Armstrong',
        'password': 'Strong1Password'
    },
    {
        'username': 'bassist',
        'email': 'usermail2@ya.ru',
        'firstname': 'Mike',
        'lastname': 'Dirnt',
        'password': 'Strong1Password'
    },
    {
        'username': 'drummer',
        'email': 'usermail3@ya.ru',
        'firstname': 'Tre',
        'lastname': 'Cool',
        'password': 'Strong1Password'
    }
)
