from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-bhhggrm(do=y4be4*e!kk351#fcf#+!$h8ioxcn4!-hoczpmhe"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "urls",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_USERNAME = "redis_username"
REDIS_PASSWORD = "123"
REDIS_HOST = "redis"

URL_SHORTENER_BASE_URL = "http://localhost:8000/u"
URL_SHORTENER_404_PAGE = "https://localhost:8000/404"
URL_SHORTENER_MAXIMUM_TOKEN_LENGTH = 5
URL_SHORTENER_MAXIMUM_URL_LENGTH = 255
URL_SHORTENER_READY_TO_SET_TOKEN_LIMIT = 10
URL_SHORTENER_MAXIMUM_RECURSION_DEPTH = 5
URL_SHORTENER_READY_TO_SET_TOKEN_URL = 'https://shayestehhs.com'
URL_SHORTENER_DEFAULT_EXPIRATION_DAYS = 365 * 5
URL_SHORTENER_READY_TO_SET_TOKEN_URL = "https://shayestehhs.com"
URL_SHORTENER_URL_PK_SEPERATOR = '<" ">'
URL_SHORTENER_DEFAULT_EXPIRATION_DAYS = 365 * 5
URL_SHORTENER_USE_CELERY_AS_USAGE_LOGGER = False
URL_SHORTENER_USE_CACHE = False
