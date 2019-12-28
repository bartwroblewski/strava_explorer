import os

from .base import *

SECRET_KEY = os.environ['SECRET_KEY']

STRAVA_CLIENT_ID = os.environ['STRAVA_CLIENT_ID']
STRAVA_CLIENT_SECRET = os.environ['STRAVA_CLIENT_SECRET']

DEBUG = False

ALLOWED_HOSTS = ['139.59.157.188']

STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)),
    'strava_collected_static',
)


