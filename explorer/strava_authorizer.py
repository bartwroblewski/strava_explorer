import os
from urllib.parse import urlencode

import requests

from django.conf import settings
from django.shortcuts import reverse

def get_auth_page_url(request):
    base = 'https://www.strava.com/oauth/authorize/?'
    params = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('explorer:authorize')),
        'response_type': 'code',
        'approval_prompt': 'force',
        'scope': 'activity:read_all',
    }
    querystring = urlencode(params)
    auth_page_url = base + querystring
    return auth_page_url
    
def exchange_code_for_tokens(code):
    token_url = 'https://www.strava.com/oauth/token'
    payload = {
        'client_id': settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }
    tokens = requests.post(token_url, data=payload).json()
    return tokens
            
