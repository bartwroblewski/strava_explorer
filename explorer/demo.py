import os
import json
import pickle

from django.conf import settings

from .models import GPXFile

def get_demo_activities():  
    path = os.path.join(
        settings.MEDIA_ROOT,
        'demo_data', 
        'demo_activities.json',
    )
    with open(path, 'r') as f:
        demo_activities = json.load(f)
    return demo_activities

def get_demo_leaderboards(activity_id):
     path = os.path.join(
        settings.MEDIA_ROOT,
        'demo_data',
        'leaderboards',
        '{}'.format(activity_id),
     )
     with open(path, 'rb') as f:
         demo_leaderboards = pickle.load(f)
     return demo_leaderboards
     
def get_only_pickled_activities(activities):
    path = os.path.join(
        settings.MEDIA_ROOT,
        'demo_data',
        'leaderboards',
    )
    pickles_ids = os.listdir(path)
    only_pickled_activities = [
        a
        for a in activities
        if str(a['id']) in pickles_ids
    ]
    return only_pickled_activities

def refresh_demo_activities(activities):
    path = os.path.join(
        settings.MEDIA_ROOT,
        'demo_data', 
        'demo_activities.json',
    )
    with open(path, 'w') as f:
        json.dump(activities, f)
        
def get_demo_gpx_options():
    files = GPXFile.objects.filter(is_demo=True)
    options = [f.file_name for f in files]
    return options
