import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get("SECRET_KEY")


DEBUG = os.environ.get("DEBUG", "False") == "True"


ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "drf_spectacular",

    "apps.users",
    "apps.wallets",
    "apps.transactions",
    "apps.authentication",
    "apps.invoices",
    "apps.splits",
    "apps.settlements",
    "apps.notifications",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": dj_database_url.config(
        default=(
            f"postgres://"
            f"{os.environ.get('POSTGRES_USER','harkarananand')}:"
            f"{os.environ.get('POSTGRES_PASSWORD','your_password')}"
            f"@{os.environ.get('POSTGRES_HOST','localhost')}:"
            f"{os.environ.get('POSTGRES_PORT','5432')}/"
            f"{os.environ.get('POSTGRES_DB','groupwallet')}"
        ),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"


TIME_ZONE = "UTC"


USE_I18N = True


USE_TZ = True


STATIC_URL = "static/"


STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTH_USER_MODEL = "users.User"


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",

    "PAGE_SIZE": 10,

    "DEFAULT_THROTTLE_RATES": {
        "anon": "5/min",
    }
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=10),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "TribePay API",

    "DESCRIPTION": """
**Your tribe. Your money. Together.**

A fintech backend system for collaborative payments, featuring:
* **Wallets:** Individual digital accounts and shared group (tribe) pools.
* **Tribes:** Shared wallet spaces with member-based collaboration.
* **Transfers:** Peer-to-peer (P2P) transaction-safe money movements.
* **Payments:** Smart payment splitting and invoice-based requests.
* **Settlements:** Optimized bilateral balance reconciliation between users.

Engineering Focus
* **Architecture:** Service-layer design with separated business logic and RESTful APIs.
* **Reliability:** Transaction-safe operations along with idempotency safeguards and automated test coverage.
* **Consistency:** Concurrency control using database transactions and row-level locking.
* **Security:** JWT authentication with API access controls and request throttling.
* **Automation:** Asynchronous processing with scheduled background workflows.

*TribePay handles your tribe's money matters, while you build relationships.*
    """,

    "VERSION": "2.1.0",

    "SERVE_INCLUDE_SCHEMA": False,

    "COMPONENT_SPLIT_REQUEST": True,
}


REDIS_URL = os.environ.get(
    "REDIS_URL",
    "redis://localhost:6379/0"
)


CELERY_BROKER_URL = REDIS_URL


CELERY_RESULT_BACKEND = REDIS_URL


CELERY_BEAT_SCHEDULE = {
    "expire-invoices": {
        "task": "apps.invoices.tasks.expire_pending_invoices",
        "schedule": 3600,
    },

    "invoice-reminders": {
        "task": "apps.invoices.tasks.send_invoice_expiry_reminders",
        "schedule": 3600,
    },
}