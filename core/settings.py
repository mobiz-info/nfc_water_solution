from datetime import timedelta
import os
from pathlib import Path
from decouple import config, Csv
import firebase_admin
from firebase_admin import credentials

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', cast=bool)
SERVER = config('SERVER', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

INSTALLED_APPS = [
    'el_pagination',
    
    'ckeditor',
    'ckeditor_uploader',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'master',
    'accounts',
    'van_management',
    'product',
    'apiservices',
    'coupon_management',
    'client_management',
    'rest_framework',
    'corsheaders',
    'customer_care',
    'order',
    'competitor_analysis',
    'tax_settings',
    'sales_management',
    'invoice_management',
    'credit_note',
    'custody',
    'bottle_management'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# cred = credentials.Certificate(BASE_DIR / config('FIREBASE_CRED_KEY'))
# firebase_admin.initialize_app(cred,name="sanawater")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if not SERVER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'autocommit': True,
            
        },
    },
    
}

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOWED_ORIGINS = [
    "http://*",
    "https://*",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ORIGIN_ALLOW_ALL = True

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # ...
]

DJANGO_WYSIWYG_FLAVOR = "ckeditor"
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'


DJANGO_WYSIWYG_FLAVOR = "ckeditor"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_UPLOAD_PATH = "uploads/"


CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'office2013',

        'height': 100,
        'width': '100%',
        'tabSpaces': 4,
        'toolbar_Custom': [
            {'name': 'math', 'items': ['Mathjax', ]},
            ['Link', 'Unlink'],
            {'name': 'document', 'items': ['Source', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Undo', 'Redo', 'PasteFromWord', '-']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-',]},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-',]},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar','PasteFromWord']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize',]},

            '/',  # put this to force next toolbar on new line
        ],
        'toolbar': 'full',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['Link', 'Unlink', 'Image'],
            ['Source'],
        ],
        'mathJaxLib': '//cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML',
        'extraPlugins': ','.join(['mathjax','uploadimage','uploadwidget','widget']),
    },
    'resize_enabled' : 'false',
}

X_FRAME_OPTIONS = 'ALLOWALL'

XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']

# InterSanaization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dubai'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'login'
LOGOUT_URL = '/app/accounts/logout/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = 'login'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


STATIC_URL = '/static/'
STATICFILES_DIRS = (BASE_DIR / 'static',)
STATIC_ROOT = (BASE_DIR / 'static'/ 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EL_PAGINATION_PREVIOUS_LABEL = "Previous"
EL_PAGINATION_NEXT_LABEL = "Next"
EL_PAGINATION_USE_NEXT_PREVIOUS_LINKS = True
EL_PAGINATION_DEFAULT_CALLABLE_EXTREMES = 1
EL_PAGINATION_DEFAULT_CALLABLE_AROUNDS = 1


# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(days=210),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=730),
#     'ROTATE_REFRESH_TOKENS': True,
#     'BLACKLIST_AFTER_ROTATION': True
# }

# REST_FRAMEWORK = {
#     'DATE_INPUT_FORMATS': [
#         'iso-8601', '%Y-%m-%d'
#         ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework_simplejwt.authentication.JWTAuthentication'
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#     ]
# }

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # In-memory (dev)
        "LOCATION": "unique-snowflake",
    }
}