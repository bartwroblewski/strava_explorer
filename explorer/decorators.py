import functools

from django.http import HttpResponse

from .models import QuotaLeft

def tokens_required(func):
    '''View decorator that ensures that Strava tokens required to
    poll Strava API are already cached in session or demo mode is on.
    '''
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        demo_mode = request.session.get('demo_mode')
        tokens = request.session.get('tokens')
        if tokens or demo_mode:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('Connect with Strava first!')
    return wrapper

#~ def check_quota_left(func):
    #~ '''Check if there is any Strava API requests quota left'''
    #~ @functools.wraps(func)
    #~ def wrapper(request, *args, **kwargs):
        #~ quota_left = QuotaLeft.objects.first()
        #~ if quota_left.per_15_minutes <= 0 or quota_left.per_day <= 0:
            #~ print('ggggggggggggggggggggg')
            #~ return HttpResponse('No more requests quota left!')
        #~ else:
            #~ return func(request, *args, **kwargs)
    #~ return wrapper
