"""
Django settings for emailsender project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os,dj_database_url,warnings,ast
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv
from decouple import config
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def get_bool_from_env(name, default_value):
    if name in os.environ:
        value = os.environ[name]
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            raise ValueError("{} is an invalid value for {}".format(value, name)) from e
    return default_value

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
if not SECRET_KEY:
    warnings.warn("SECRET_KEY not configured, using a random temporary key.")
    SECRET_KEY = get_random_secret_key()

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'home',
    'authentication'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'tinymce',  
    'django_extensions',
    'corsheaders',
    
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'emailsender_core.urls'
SETTINGS_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH,'templates')],
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


WSGI_APPLICATION = 'emailsender_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
load_dotenv()
try:
    database_port = int(os.environ.get('DATABASE_PORT', '5432'))
except ValueError as e:
    raise ValueError(f"Port could not be cast to integer value: {e}")

DATABASES = {
    'default': dj_database_url.config(
        default=f"postgresql://{config('DATABASE_USER')}:{config('DATABASE_PASSWORD')}@{config('DATABASE_HOST', 'localhost')}:{config('DATABASE_PORT', '5432')}/{config('DATABASE_NAME')}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

""" EMAIL CONFIGURATIONS"""


EMAIL_HOST_USER       = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD   = config('EMAIL_HOST_PASSWORD')

EMAIL_BACKEND         = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST            = config('EMAIL_HOSTS')
RECIEVER_EMAIL        = config('RECIEVER_EMAIL')

EMAIL_DOMAIN          = config('EMAIL_DOMAIN')
EMAIL_PORT            = config('EMAIL_PORT')

EMAIL_USE_TLS         = config('EMAIL_USE_TLSS', default=False, cast=bool)
EMAIL_USE_SSL         = config('EMAIL_USE_SSLS', default=False, cast=bool)

DEFAULT_FROM_EMAIL    = config('DEFAULT_FROM_EMAIL')

TRACKING_SERVER       = config('TRACKING_SERVER', default=None)
UNSUBSCRIPTION_PATH   = config('UNSUBSCRIPTION_PATH')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if DEBUG else []

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


LOGIN_URL = '/auth/login/'

AUTH_USER_MODEL  = 'authentication.Users'




