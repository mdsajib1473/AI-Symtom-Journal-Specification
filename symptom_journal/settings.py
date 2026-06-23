"""
Django settings for the symptom_journal project.

P1 - foundation only. All environment-specific configuration is read from a
local .env file (see .env.example for the required keys) via python-dotenv.
"""

import os
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env (kept out of version control).
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-.env")

# Treat common truthy strings as True; everything else (incl. unset) is False.
DEBUG = os.getenv("DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# Comma-separated, e.g. "localhost,127.0.0.1,my-app.onrender.com"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

# Origins trusted for CSRF-protected requests behind HTTPS (Render).
# Comma-separated with scheme, e.g. "https://my-app.onrender.com"
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Jazzmin must precede django.contrib.admin to theme the admin.
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "apps.checker",
    "apps.accounts",
    "apps.history",
    "apps.feedback",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise must come immediately after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "symptom_journal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "symptom_journal.wsgi.application"


# ---------------------------------------------------------------------------
# Database (PostgreSQL via DATABASE_URL)
# ---------------------------------------------------------------------------
def parse_database_url(url):
    """
    Turn a postgres:// connection string into a Django DATABASES entry.

    We parse manually rather than using urllib.parse.urlparse because a raw
    password containing reserved characters (e.g. '#') silently breaks
    urlparse. Percent-encoded values are still decoded via unquote, so both
    raw and URL-encoded passwords are accepted.
    Format: postgresql://USER:PASSWORD@HOST:PORT/NAME[?params]
    """
    _, _, rest = url.partition("://")
    rest = rest.split("?", 1)[0]                 # drop any query string
    userinfo, _, hostinfo = rest.rpartition("@")
    user, _, password = userinfo.partition(":")
    hostport, _, name = hostinfo.partition("/")
    host, sep, port = hostport.rpartition(":")
    if not sep:                                  # no ":port" supplied
        host, port = hostport, "5432"
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(name),
        "USER": unquote(user),
        "PASSWORD": unquote(password),
        "HOST": unquote(host),
        "PORT": port,
    }


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
    )
DATABASES = {"default": parse_database_url(DATABASE_URL)}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (served by WhiteNoise in production)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Plain storage in development; compressed + hashed in production so
        # WhiteNoise can serve assets with far-future cache headers.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------------
# Authentication redirects
# ---------------------------------------------------------------------------
LOGIN_REDIRECT_URL = "/check/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Jazzmin admin theme (admin appearance only - no app behaviour changes)
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    # Window title and brand
    "site_title": "SymptomAI Admin",
    "site_header": "SymptomAI",
    "site_brand": "SymptomAI",
    "welcome_sign": "Welcome to SymptomAI Research Dashboard",
    "copyright": "MD SAJIB AHAMMAD",

    # Top search bar - search users and symptom checks
    "search_model": ["auth.user", "checker.symptomcheck"],

    # Icons for each model - use Font Awesome 5 free icons
    "icons": {
        "auth.user": "fas fa-users",
        "checker.symptomcheck": "fas fa-heartbeat",
        "feedback.feedback": "fas fa-star",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # Top navigation links
    "topmenu_links": [
        {"name": "Live Site", "url": "/", "new_window": True},
        {"name": "Check Symptoms", "url": "/check/", "new_window": True},
    ],

    # UI tweaks
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "auth",
        "checker",
        "feedback",
    ],

    # Links at the bottom of the sidebar
    "usermenu_links": [
        {"name": "Live Site", "url": "/", "new_window": True},
    ],

    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-teal",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-teal",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
