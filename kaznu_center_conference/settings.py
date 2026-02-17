import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = str(os.getenv("DEBUG")) == "1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ckeditor_5',
    'conferences',
    'django_recaptcha',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kaznu_center_conference.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'conferences.context_processors.latest_conference',
                'conferences.context_processors.base_site',
            ],
        },
    },
]

WSGI_APPLICATION = 'kaznu_center_conference.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

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

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russian')),
    ('en', gettext('English')),
    ('kk', gettext('Kazakh')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en', 'kk')

MODELTRANSLATION_CUSTOM_FIELDS = ('CKEditor5Field',)

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'bulletedList', 'numberedList', 'blockQuote', '|',
            'insertTable', 'mediaEmbed', '|',
            'sourceEditing',
            '|', 'undo', 'redo',
            '|', 'fontSize', 'fontColor', 'fontBackgroundColor'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties' ],
        },
        'heading': {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'htmlSupport': {
            'allow': [
                {'name': '/.*/', 'attributes': True, 'classes': True, 'styles': True}
            ]
        }
    }
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

AUTHENTICATION_BACKENDS = [
    'conferences.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'conferences.User'

LOGIN_URL = 'conferences:login'

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

LOGIN_REDIRECT_URL = 'conferences:profile'

LOGOUT_REDIRECT_URL = 'conferences:detail'

BASE_SITE = os.getenv('BASE_SITE')

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')

RECAPTCHA_USE_SSL = True

SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'conferences': { 
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}