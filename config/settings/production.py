# ruff: noqa: E501
import os
from collections.abc import Mapping

from .base import *  # noqa: F403
from .base import DATABASES
from .base import INSTALLED_APPS
from .base import REDIS_URL
from .base import env


def _normalize_coolify_host(raw_host: str) -> str:
    cleaned = raw_host.strip()
    if not cleaned or cleaned.startswith("$"):
        return ""
    if "://" in cleaned:
        cleaned = cleaned.split("://", 1)[1]
    cleaned = cleaned.split("/", 1)[0]
    if ":" in cleaned and not cleaned.startswith("["):
        cleaned = cleaned.split(":", 1)[0]
    return cleaned


def _normalize_coolify_origin(raw_url: str) -> tuple[str, str]:
    cleaned = raw_url.strip().rstrip("/")
    if not cleaned or cleaned.startswith("$"):
        return "", ""
    if not cleaned.startswith(("http://", "https://")):
        return "", ""
    scheme, rest = cleaned.split("://", 1)
    host_port = rest.split("/", 1)[0]
    host_only = (
        host_port.split(":", 1)[0]
        if ":" in host_port and not host_port.startswith("[")
        else host_port
    )
    origin_host = host_only if host_port.endswith(":5000") else host_port
    return host_only, f"{scheme}://{origin_host}"


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _expand_host_origins(allowed_hosts: list[str], csrf_origins: list[str]) -> None:
    local_only = {"*", "localhost", "127.0.0.1", "[::1]"}
    for host in allowed_hosts:
        if host in local_only or host.startswith("."):
            continue
        _append_unique(csrf_origins, f"https://{host}")
        _append_unique(csrf_origins, f"http://{host}")


def build_coolify_hosts_and_origins(
    environ_map: Mapping[str, str] | None = None,
) -> tuple[list[str], list[str], bool]:
    """
    Resolve ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, and whether HTTPS cookies should be
    enabled by default from standard Django and Coolify magic environment variables.
    """
    source = environ_map if environ_map is not None else os.environ
    allowed_hosts: list[str] = []
    csrf_origins: list[str] = []

    host_keys = (
        "DJANGO_ALLOWED_HOSTS",
        "COOLIFY_FQDN",
        "SERVICE_FQDN_DJANGO",
        "SERVICE_FQDN_DJANGO_5000",
    )
    for raw_part in (p for k in host_keys for p in source.get(k, "").split(",")):
        _append_unique(allowed_hosts, _normalize_coolify_host(raw_part))

    url_keys = (
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "COOLIFY_URL",
        "SERVICE_URL_DJANGO",
        "SERVICE_URL_DJANGO_5000",
    )
    for raw_part in (p for k in url_keys for p in source.get(k, "").split(",")):
        host_only, origin = _normalize_coolify_origin(raw_part)
        _append_unique(allowed_hosts, host_only)
        _append_unique(csrf_origins, origin)

    for default_host in ("web-result.shawon.me", "localhost", "127.0.0.1", "[::1]"):
        _append_unique(allowed_hosts, default_host)

    _expand_host_origins(allowed_hosts, csrf_origins)

    coolify_urls = [
        u.strip()
        for key in ("COOLIFY_URL", "SERVICE_URL_DJANGO", "SERVICE_URL_DJANGO_5000")
        for u in source.get(key, "").split(",")
        if u.strip() and not u.strip().startswith("$")
    ]
    default_secure_cookies = (
        any(u.startswith("https://") for u in coolify_urls) if coolify_urls else True
    )
    return allowed_hosts, csrf_origins, default_secure_cookies


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
_raw_secret = env("DJANGO_SECRET_KEY", default="").strip()
if not _raw_secret or _raw_secret.startswith("$"):
    _raw_secret = env("SERVICE_BASE64_64_DJANGO", default="").strip()
SECRET_KEY = (
    _raw_secret
    if (_raw_secret and not _raw_secret.startswith("$"))
    else "change-me-in-production-web-result-secret-key"
)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, _DEFAULT_SECURE_COOKIES = (
    build_coolify_hosts_and_origins()
)

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# CACHES
# ------------------------------------------------------------------------------
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "",
        },
    }

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Coolify's Traefik reverse proxy handles HTTP->HTTPS redirection at the edge.
# Exempt /healthz/ so internal Docker HTTP healthchecks never receive a 301 redirect.
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SECURE_REDIRECT_EXEMPT = [r"^healthz/?$"]
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = env.bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    default=_DEFAULT_SECURE_COOKIES,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME = "__Secure-sessionid" if SESSION_COOKIE_SECURE else "sessionid"
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = env.bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    default=_DEFAULT_SECURE_COOKIES,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = "__Secure-csrftoken" if CSRF_COOKIE_SECURE else "csrftoken"
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

# STATIC & MEDIA
# ------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="Web Result <noreply@web-result.shawon.me>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[Web Result] ",
)
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

# Anymail
# ------------------------------------------------------------------------------
MAILGUN_API_KEY = env("MAILGUN_API_KEY", default="")
if MAILGUN_API_KEY:
    INSTALLED_APPS += ["anymail"]
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = {
        "MAILGUN_API_KEY": MAILGUN_API_KEY,
        "MAILGUN_SENDER_DOMAIN": env("MAILGUN_DOMAIN", default=""),
        "MAILGUN_API_URL": env("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
    }

# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}
