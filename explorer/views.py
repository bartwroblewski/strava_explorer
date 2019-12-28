import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from .models import GPXFile, QuotaLeft

from explorer import (
    charts,
    clients,
    strava_authorizer,
    tree,
    demo,
    helpers,
)
from .decorators import tokens_required

def index(request):
    return render(request, 'explorer/index.html')
    
def authorize(request):
    '''Redirect user to Strava login/authorization page,
    obtain code and then exchange the obtained code for tokens.
    Cache obtained tokens in the session and redirect to 
    "cache_athlete activities".
    '''
    code = request.GET.get('code')
    if code:
        tokens = strava_authorizer.exchange_code_for_tokens(code)
        request.session['tokens'] = tokens
        return redirect('explorer:waiting_screen')
    else:
        # if not yet authorized, just display the authorize page
        auth_page_url = strava_authorizer.get_auth_page_url(request)
        return redirect(auth_page_url)
        
def toggle_demo_mode(request):
    request.session['demo_mode'] = True
    request.session['user_firstname'] = ''
    return redirect('explorer:cache_athlete_activities')
        
def waiting_screen(request):
    '''Display wait message while acitivities are being downloaded
    and redirect (from within template) to explorer afterwards.
    '''
    request.session['demo_mode'] = False
    request.session['user_firstname'] = request.session['tokens']['athlete']['firstname']
    return render(request, 'explorer/waiting_screen.html')
    
@tokens_required
def cache_athlete_activities(request):
    '''Poll Strava API for all athlete's activities
    and then put them in the session so that
    they are available anywhere in the app.
    Redirect to explorer afterwards.
    '''
    if request.session['demo_mode'] == True:
        all_athlete_activities = demo.get_demo_activities()
    else:
        access_token = request.session['tokens']['access_token']
        
        # date to start fetching from
        user_creation_date = helpers.timestamp(
            request.session['tokens']['athlete']['created_at'] 
        )
        
        all_athlete_activities = clients.AthleteActivities().get(
            token=access_token,
            after=user_creation_date,
        )
    request.session['activities'] = all_athlete_activities
    
    #~ # uncomment to refresh demo activities
    #~ demo.refresh_demo_activities(all_athlete_activities)
    
    return redirect('explorer:explorer')
    
@tokens_required
def explorer(request):
    return render(request, 'explorer/explorer.html')
    
@tokens_required
def leaderboards(request):
    activities = request.session['activities']
    if request.session['demo_mode'] == True:
        activities = demo.get_only_pickled_activities(activities)
    options = helpers.get_leaderboards_options(activities)
    context = {'options': options}
    return render(request, 'explorer/leaderboards.html', context)
  
@tokens_required
def have_I_been_there(request):
    '''Shows the intersection between 
    activities polylines and uploaded GPX
    '''
    dm = request.session['demo_mode']
    if request.method == 'GET':
        context = {
            'demo_mode': json.dumps(dm),
        }
        if dm == True:
            context['options'] = demo.get_demo_gpx_options()
        return render(request, 'explorer/have_I_been_there.html', context)
    elif request.method == 'POST':
        if dm == True:
            filename = request.POST.get('filename')
            uploaded_gpx = GPXFile.objects.filter(file_name=filename)[0]
        else:
            uploaded_gpx = GPXFile()        
            uploaded_gpx.file = request.FILES['file']
            uploaded_gpx.save()
            
        radius = request.POST.get('radius', 'Error getting radius!')
        activities = request.session['activities']
        lines = tree.get_lines(uploaded_gpx, activities, radius)

        response = {
            'lines': [line.to_dict() for line in lines],
            'demo_mode': dm,
            'coordinates': uploaded_gpx.decode(),
        }
        return JsonResponse(response)
        
@tokens_required
def explorer_data(request):
    activities = request.session['activities']
    inputs = dict(request.GET)
    data = charts.get_data(activities)
    user_cols = list(data)
    
    #~ if not inputs['heatmap_z_name'][0] in user_cols or not inputs['map_layer'][0] in user_cols:
            #~ response = {'message': 'Your activities do not contain this data'}
    #~ else:
    filtered_data = charts.fltr(data, inputs)    
    map_data = charts.get_map_data(filtered_data)
    map_data = charts.add_polyline_heat(map_data, inputs)
    
    pan_bounds = charts.get_pan_bounds(map_data)

    map_= charts.Map(map_data)
    heatmap = charts.Heatmap(data, inputs)
    table = charts.Table(filtered_data)
    response = {
        'heatmap': heatmap.to_dict(),
        'map': map_.to_list(),
        'map_pan_bounds': pan_bounds,
        'table': table.to_list(),
        'allowed_select_options': user_cols + ['off'],
    }
    return JsonResponse(response)
    
@tokens_required
def leaderboards_data(request):
    activity_id = request.GET.get('activity_id', 'Error getting activity ID!')
    date_ranges = request.GET.get('date_ranges', 'Error getting date ranges!').split(',')
     
    if request.session.get('demo_mode'):
        leaderboards = demo.get_demo_leaderboards(activity_id)
    else:
        token = request.session['tokens']['access_token']
        activity = clients.Activity(activity_id).get_segments(token)
        #~ segments_polylines = clients.async_get_segments_polylines(activity.segments, token)
        segments_polylines = clients.SegmentsPolylines(activity.segments).get(token)
        
        for segment in activity.segments:
            segment.polyline = segments_polylines[segment.id]

        #~ leaderboards = clients.async_get_leaderboards(
            #~ date_ranges,
            #~ token,
            #~ activity.segments,
        #~ )   
        
        leaderboards = clients.SegmentLeaderboards(
            activity.segments,
            date_ranges,
        ).get(token)
        
        #~ # uncomment to add leaderboard to demo leaderboards
        #~ import pickle
        #~ leaderboards.pickle(activity_id)
        
        leaderboards = leaderboards.leaderboards
    
    response = {
        'segment_leaderboards': [l.as_dict() for l in leaderboards],
        'request_quota_left': list(QuotaLeft.objects.all().values()),
    }
    
    return JsonResponse(response)   

def flush_session(request):
    request.session.flush()
    return HttpResponse('Session flushed')
