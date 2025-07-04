# -*- coding: utf-8 -*-
from placeholder.settings.base import *  # noqa: F403, F401

DEBUG = True

CORS_ALLOWED_ORIGINS = [
    "api.place-holder.site",
]

ALLOWED_HOSTS = ["api.place-holder.site"]

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # noqa: F405
]
