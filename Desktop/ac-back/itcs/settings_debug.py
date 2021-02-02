import os
from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import BASE_DIR

DEBUG = True
DATABASE_ROUTERS = ['itcs.database_routing.AuthRouter']

JWT_AUTH_KEY = 'vg*aa3&e9au97=z)oibiv-&1g3!z!tr&y4d$rk3@vrffm&v2!s'

DATABASES = {
    'default': {
        'HOST': os.getenv('MAIN_DATABASE_HOST', '172.16.1.229'),
        'USER': os.getenv('MAIN_DATABASE_USER', 'itcs_u'),
        'PASSWORD': os.getenv('MAIN_DATABASE_PASSWORD', 'PasSWordishe5'),
        'NAME': os.getenv('MAIN_DATABASE_NAME', 'itcs_main'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'PORT': os.getenv('MAIN_DATABASE_PORT', '5432'),
        'PGCRYPTO_KEY': 'R438&*fqo&bll0bb3c6ijKF^5X3vsSw^H*LOE@R'
    },
    'keys_communcation': {
        'NAME': os.getenv('COMMUNICATION_NAME', 'communication'),
        'HOST': os.getenv('COMMUNICATION_HOST', '172.16.1.229'),
        'USER': os.getenv('COMMUNICATION_USER', 'itcs_u'),
        'PASSWORD': os.getenv('COMMUNICATION_PASSWORD', 'PasSWordishe5'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'PORT': os.getenv('COMMUNICATION_PORT', '5432'),
    },
}

MIDDLEWARE = [
    # 'elasticapm.contrib.django.middleware.TracingMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'querycount.middleware.QueryCountMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SWAGGER_SETTINGS = {
    'PERSIST_AUTH': True,
    'DEEP_LINKING': False,
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

INSTALLED_APPS = [
    'clearcache',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'gm2m',
    'core',
    'taggit',
    'yubikey_api_auth',
    'docs',
    'drf_yasg',
    'directory',
    'corsheaders',
    'sailor',
    'communication',
    'pgcrypto',
    'user_profile',
    'verification',
    'personal_cabinet',
    'sms_auth',
    'news',
    'reports',
    'payments',
    'idgovua_auth',
    'delivery',
    'public_api',
    'cadets',
    'signature',
    'back_office',
    'certificates',
    'agent',
    'notifications',
    'sailor.statement',
    'sailor.document',
    'payments.platon',
    'reports.back_office_report',
    'training',
    'cacheops',
]

# ELASTIC_APM = {
#     'SERVICE_NAME': f'AC-ITCS-{os.getenv("PROJECT_ENV", "localhost")}',
#     'DEBUG': True,
#     'SERVER_URL': 'http://10.64.10.72:8200'
# }

sentry_sdk.init(
    integrations=[DjangoIntegration()],
    dsn='http://e487884f95b3434ba4bc87d27153db35@10.64.10.77:9000/2',
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'itcs.ExpireToken.ExpiringTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DATETIME_FORMAT': '%H:%M:%S %d.%m.%Y',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

SIMPLE_JWT = {
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=15),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': JWT_AUTH_KEY
}

PAYGOVUA_TEST_MODE = True

PAYGOVUA_URL = 'https://dev.pay.gov.ua:12443/ecomm/v1.0/'
PAYGOVUA_MERCHANT_NAME = 'CabinetMoraka_test'
PAYGOVUA_PUBLIC_KEY = './payments/keys/CabinetMoraka_test_PublicKey.key'
PAYGOVUA_OWN_PRIVATE_KEY = './payments/keys/disoft_paygovua_pr.pem'

if not os.path.exists(os.path.join(BASE_DIR, 'logs/ntz')):
    try:
        os.mkdir(os.path.join(BASE_DIR, 'logs'), 644)
    except Exception:
        pass
    os.mkdir(os.path.join(BASE_DIR, 'logs/ntz'), 644)
if not os.path.exists(os.path.join(BASE_DIR, 'logs/payments')):
    os.mkdir(os.path.join(BASE_DIR, 'logs/payments'), 644)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}]-{levelname}-{name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # 'payments_file': {
            # 'class': 'logging.FileHandler',
            # 'filename': os.path.join(BASE_DIR, 'logs/payments/payment.log'),
            # 'formatter': 'verbose',
        # },
        # 'ntz_file': {
            # 'class': 'logging.FileHandler',
            # 'filename': os.path.join(BASE_DIR, 'logs/payments/ntz_cert.log'),
            # 'formatter': 'verbose',
        # },
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash.TCPLogstashHandler',
            'host': '10.64.10.72',
            'port': 5000,
            'version': 1,
            'message_type': f'AC-ITCS-{os.getenv("PROJECT_ENV", "localhost")}',
            'fqdn': False,
            'tags': ['django', f'AC-ITCS-{os.getenv("PROJECT_ENV", "localhost")}']
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['logstash'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['logstash'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        # 'ac-back.payments': {
            # 'handlers': ['console', 'payments_file'],
            # 'level': 'INFO',
            # 'propagate': True
        # },
        # 'ac-back.ntz_cert': {
           # 'handlers': ['console', 'ntz_file'],
           # 'level': 'DEBUG',
           # 'propagate': True
        },
    }

PHONE_TO_ADDITIONAL_VERIFICATION = '+380506673966'
EMAIL_TO_ADDITIONAL_VERIFICATION = 'i.golubev@disoft.us'

ENABLE_DUPLICATE_DATA_TO_INSPECTION = os.environ.get('DUPLICATE_DATA', 'false')
if ENABLE_DUPLICATE_DATA_TO_INSPECTION == 'true':
    INSTALLED_APPS += ['inspection']
    DATABASES.update({'inspection': {
        'NAME': os.getenv('INSPECTION_NAME', 'inspection'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.getenv('INSPECTION_HOST', '172.16.1.229'),
        'PORT': os.getenv('INSPECTION_PORT', '5432'),
        'USER': os.getenv('INSPECTION_USER', 'itcs_u'),
        'PASSWORD': os.getenv('INSPECTION_PASSWORD', 'PasSWordishe5'),
        'PGCRYPTO_KEY': 'R438&*fqo&bll0bb3c6ijKF^5X3vsSw^H*LOE@R',
    }
    })

try:
    from .local_settings import *
except Exception:
    pass
