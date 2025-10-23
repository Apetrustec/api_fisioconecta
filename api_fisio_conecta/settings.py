from firebase_admin import credentials, auth, firestore
import firebase_admin
# from kombu import Queue
import os
import json
import warnings
from google.cloud import storage
from google.oauth2 import service_account
from google.auth import credentials as auth_credentials
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

load_dotenv()


# avisos de importação
# warnings.filterwarnings ( " ignore " , message = " No directory at " , module = " whitenoise.base " )

SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret! ESSA É DO FISIO CONECTA
SECRET_KEY = 'django-insecure-q-%zag7b0m85!#juwj5+ar9irfeoujss7&i%29fwfwf3t5m*te'


PROJECT_ROOT = 'django_fisio/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
# SECURED_FIELDS_KEY= os.getenv('SECURED_FIELDS_KEY', 'vCWuo9XQAKit2NP4XlLdciOWl3AaP6nKmaCnnbSCrIY=')
# SECURED_FILDS_HASH_SALT=os.getenv('SECURED_FILDS_HASH_SALT', '3de5f3de')


# SECURITY WARNING: don't run with debug turned on in production!
#
# DEBUG = False
DEBUG = os.getenv('GLOBAL_CONFIG_DEBUG', False)
ASSOCIATED_DOMAIN = os.getenv('GLOBAL_CONFIG_ASSOCIATED_DOMAIN', 'testeapetrus.page.link')


# ALLOWED_HOSTS = [
#     '127.0.0.1',
#     'localhost',
#     '192.168.1.100'  # Adicione seu IP local ou outro host que você deseja permitir
# ]
ALLOWED_HOSTS = [('*')]

INSTALLED_APPS = [
    'pipeline',
    'corsheaders',
    'rest_framework',
    'secured_fields',
    'fisio_conecta',
    'django_extensions',
    # 'django_filters', resolve problema template does not exists
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django_brotli.middleware.BrotliMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

if not DEBUG:
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 4
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
else:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None


# if not DEBUG:
#     CORS_ORIGIN_ALLOW_ALL = False
#     CORS_ORIGIN_WHITELIST = (
#         'https://api.userede.com.br',
#         'https://api.cieloecommerce.cielo.com.br',
#         'https://app.apetrus.com.br',
#         'https://postos.apetrus.com.br',
#         'https://admin.apetrus.com.br',
#         'https://frentista.apetrus.com.br',
#         'https://empresas.apetrus.com.br',
#         'https://cadastros.apetrus.com.br',
#         'https://teste-app.apetrus.com.br',
#         'https://teste-postos.apetrus.com.br',
#         'https://teste-admin.apetrus.com.br',
#         'https://teste-frentista.apetrus.com.br',
#         'https://teste-empresas.apetrus.com.br',
#         'https://teste-cadastros.apetrus.com.br',
#         'https://teste-convenios.apetrus.com.br',
#         'https://api.userede.com.br',
#         'https://cieloecommerce.cielo.com.br',
#         'https://app.apetrus.com.br',
#         'https://postos.apetrus.com.br',
#         'https://admin.apetrus.com.br',
#         'https://frentista.apetrus.com.br',
#         'https://empresas.apetrus.com.br',
#         'https://cadastros.apetrus.com.br',
#         'https://convenios.apetrus.com.br',
#         'https://teste-app.apetrus.com.br',
#         'https://teste-postos.apetrus.com.br',
#         'https://teste-admin.apetrus.com.br',
#         'https://teste-frentista.apetrus.com.br',
#         'https://teste-empresas.apetrus.com.br',
#         'https://teste-cadastros.apetrus.com.br',
#         'https://teste-convenios.apetrus.com.br',
#         'http://157.230.221.177',
#         'http://127.0.0.1:8000',
#         'http://192.168.1.101:8000',
#         'http://localhost:8000',
#         'http://localhost:8080',
#         'http://localhost:8081',
#         'http://localhost:8082',
#         'http://localhost:8095',
#         'http://192.168.100.45'
#     )
# else:
#     CORS_ORIGIN_ALLOW_ALL = True


# CSRF_TRUSTED_ORIGINS = (
#     'https://api.userede.com.br',
#     'https://app.apetrus.com.br',
#     'https://api.cieloecommerce.cielo.com.br',
#     'https://postos.apetrus.com.br',
#     'https://admin.apetrus.com.br',
#     'https://frentista.apetrus.com.br',
#     'https://empresas.apetrus.com.br',
#     'https://cadastros.apetrus.com.br',
#     'https://teste-app.apetrus.com.br',
#     'https://teste-postos.apetrus.com.br',
#     'https://teste-admin.apetrus.com.br',
#     'https://teste-frentista.apetrus.com.br',
#     'https://teste-empresas.apetrus.com.br',
#     'https://teste-cadastros.apetrus.com.br',
#     'https://teste-convenios.apetrus.com.br',
#     'https://api.userede.com.br',
#     'https://cieloecommerce.cielo.com.br',
#     'https://app.apetrus.com.br',
#     'https://postos.apetrus.com.br',
#     'https://admin.apetrus.com.br',
#     'https://frentista.apetrus.com.br',
#     'https://empresas.apetrus.com.br',
#     'https://cadastros.apetrus.com.br',
#     'https://convenios.apetrus.com.br',
#     'https://teste-app.apetrus.com.br',
#     'https://teste-postos.apetrus.com.br',
#     'https://teste-admin.apetrus.com.br',
#     'https://teste-frentista.apetrus.com.br',
#     'https://teste-empresas.apetrus.com.br',
#     'https://teste-cadastros.apetrus.com.br',
#     'https://teste-convenios.apetrus.com.br',
#     'http://157.230.221.177',
#     'http://127.0.0.1:8000',
#     'http://192.168.1.101:8000',
#     'http://localhost:8000',
#     'http://localhost:8080',
#     'http://localhost:8081',
#     'http://localhost:8082',
#     'http://localhost:8095',
#     'http://192.168.100.45'
# )

ROOT_URLCONF = 'api_fisio_conecta.urls' # PRECISA OLHAR ISSO Dps

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

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}

WSGI_APPLICATION = 'api_fisio_conecta.wsgi.application' # PRECISA OLHAR ISSO Dps


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases


DB_NAME = os.getenv('POSTGRES_DB', 'fisio_conecta')
DB_USER = os.getenv('POSTGRES_USER', 'apetrus')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'apetrus20')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_HOST_REPLICA = os.getenv('POSTGRES_HOST_REPLICA', 'localhost')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,  # Nome do banco de dados
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '5432',
    },
    'replica': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME, # Nome do banco de dados
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST_REPLICA,
        'PORT': '5432',
	}
}

# DATABASE_ROUTERS = ['desenv.database_router.DatabaseRouter'] #OLHAR ISSO DPS


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

PIPELINE = {
    'PIPELINE_ENABLED': True
}

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Recife'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_build')
]


credenciais_fisio_conecta = 'fisio-conecta-producao.json'

credenciais_fisio_conecta_cred = credentials.Certificate(credenciais_fisio_conecta)

firebase_admin.initialize_app(
    credenciais_fisio_conecta_cred,
    name='fisio_conecta',
    options={
        'auth_token_validity_leeway': 300  # 5 minutos de tolerância
    }
)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

