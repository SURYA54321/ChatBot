"""
Django settings for config project.
"""

from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-development-key",
)

DEBUG = os.getenv(
    "DEBUG",
    "True",
).lower() == "true"

# >>> CHANGED: was an empty list, which would reject every request
# once DEBUG=False in production. Reads from an env var so you can
# set the real Render domain without touching code.
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com"
).split(",")

# Dynamically add Render's external hostname if available
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "rest_framework",
    "corsheaders",

    "accounts",
    "conversations",
    "documents",
    "chat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    # >>> NEW: serves static files (Django admin CSS/JS) directly
    # from Django in production, since Render's free tier has no
    # separate static file server.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# >>> CHANGED: DB path now points into a subfolder so it can live on
# Render's persistent disk (mounted at /var/data in the next step).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv(
            "SQLITE_PATH",
            str(BASE_DIR / 'db.sqlite3'),
        ),
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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'

# >>> NEW: required for collectstatic (Render runs this during
# build) and for whitenoise to actually find/serve files.
STATIC_ROOT = BASE_DIR / "staticfiles"

# >>> NEW: enables compression + far-future caching headers for
# static files, standard whitenoise production setup.
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# >>> REMOVED: MAILERS was never a real Django setting (Django uses
# EMAIL_BACKEND). Left out entirely — dead config, not used anywhere
# in the codebase.


# >>> CHANGED: was CORS_ALLOW_ALL_ORIGINS = True (fine for dev,
# unsafe in production). Now reads a comma-separated list from an
# env var — set this to your Vercel URL once deployed.
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173",
).split(",")


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


MEDIA_URL = "/media/"
# >>> CHANGED: same reasoning as SQLITE_PATH — needs to live on the
# persistent disk so uploaded documents survive redeploys.
MEDIA_ROOT = Path(
    os.getenv(
        "MEDIA_ROOT",
        str(BASE_DIR / "media"),
    )
)