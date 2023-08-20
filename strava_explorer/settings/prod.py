import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['46.101.156.79']

STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)),
    'strava_collected_static',
)


