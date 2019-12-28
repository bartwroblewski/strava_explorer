import os
import pickle
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession

from django.conf import settings

from .charts import decode_polyline
from .models import QuotaLeft

class StravaApiRequest:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://www.strava.com/api/v3/'
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
        }
        self.quota_left = QuotaLeft()
    
    def get(self):
        response = requests.get(self.url, params=self.params, headers=self.headers)
        
        # keep track of available request quota 
        self.quota_left.update(response)
        #~ print(repr(self), repr(self.quota_left))
        
        return response
        
    async def async_get(self, session):
        response = await session.request(method="GET", url=self.url, params=self.params, headers=self.headers)
        jsn = await response.json()
        
        # keep track of available request quota 
        self.quota_left.update(response)
        #~ print(repr(self), repr(self.quota_left))
        
        return jsn
        
    def __repr__(self):
        return '\nRequested {}'.format(self.url) 
        
class AthleteActivitiesRequest(StravaApiRequest):
    def __init__(self, access_token, after, page):
        super().__init__(access_token)
        self.params = {
            'page': page,
            'per_page': 200,
            'after': after,
        }
        self.after = after
        self.url = '{}athlete/activities'.format(self.base_url)
                
class ActivityRequest(StravaApiRequest):
    def __init__(self, access_token, activity_id):
        super().__init__(access_token)
        self.params = {
            'include_all_efforts': True,
        }
        self.url = '{}activities/{}'.format(self.base_url, activity_id)
        
class SegmentRequest(StravaApiRequest):
    def __init__(self, access_token, segment_id):
        super().__init__(access_token)
        self.params = {
            'id': segment_id,
            }
        self.url = '{}segments/{}'.format(self.base_url, segment_id)
        
class SegmentLeaderboardRequest(StravaApiRequest):
    def __init__(self, access_token, segment_id, date_range):
        super().__init__(access_token)
        self.params = {
            'id': segment_id,
            'date_range': date_range,
            }
        self.url = '{}segments/{}/leaderboard'.format(self.base_url, segment_id)

class Segment:
    def __init__(self, id, name, hazardous):
        self.id = id 
        self.name = name
        self.hazardous = hazardous  
        self.polyline = []   
        self.strava_link = 'https://www.strava.com/segments/{}'.format(self.id)
           
    async def get_polyline(self, token, session):
        request = SegmentRequest(token, self.id)
        response = await request.async_get(session)
        polyline = decode_polyline(response['map']['polyline'])
        return polyline 
        
    async def get_leaderboard(self, token, session, date_range):
        request = SegmentLeaderboardRequest(token, self.id, date_range)
        response = await request.async_get(session)
        entries = response['entries']
        leaderboard = SegmentLeaderboard(self, entries)
        return leaderboard

    #~ def get_leaderboards(self, date_ranges, token):
        #~ leaderboards = []
        #~ for date_range in date_ranges:
            #~ request = SegmentLeaderboardRequest(token, self.id, date_range)
            #~ response = request.get().json()
            #~ leaderboard = SegmentLeaderboard(
                    #~ self.name, 
                    #~ date_range,
                    #~ response['entries'],
                #~ )
            #~ leaderboards.append(leaderboard)      
        #~ return leaderboards


        
class Activity:
    def __init__(self, id, segments=None):
        self.id = id
        self.segments = segments

    #~ def bulk(self):
        #~ '''Generator passed to asyncio loop'''
        #~ for segment in self.segments:
            #~ # Strava blocks downloading leaderboards
            #~ # for hazardous segments
            #~ if not segment.hazardous:
                #~ yield segment.id, segment.name, segment.polyline
              
    def get_segments(self, token):
        request = ActivityRequest(token, self.id)
        response = request.get().json()
        segments = []
        for se in response['segment_efforts']:
            segment_id = se['segment']['id']
            #~ req = SegmentRequest(token, segment_id)
            #~ segment_polyline = req.get().json()['map']['polyline']
            segment = Segment(
                segment_id,
                se['segment']['name'],
                se['segment']['hazardous'],
                #~ segment_polyline,
            )
            segments.append(segment)
        return self.__class__(self.id, segments)
        
class AthleteActivities:
    def __init__(self):
        self.all_activities = []
        self.page = 1 # start fetching at first page by default   
    
    def get(self, token, after):
        request = AthleteActivitiesRequest(token, after, self.page)
        
        per_page_activities = request.get().json()
        self.all_activities += per_page_activities
        
        if len(per_page_activities) == request.params['per_page']:
            # if next page might exist, fetch it
            self.page += 1
            self.get(token, after)
            
        return self.all_activities
        
class SegmentLeaderboard:
    def __init__(self, segment, entries):
        self.segment  = segment
        self.segment_name = segment.name
        self.segment_polyline = segment.polyline
        self.entries = entries

    def as_dict(self):
        '''Makes instance serializable'''
        d = {
            'segment_name': self.segment_name,
            'segment_polyline': self.segment_polyline,
            'segment_strava_link': self.segment.strava_link,
            'entries': self.entries,
            
        }
        return d
        
class SegmentLeaderboards:
    def __init__(self, segments, date_ranges):
        self.segments = segments
        self.date_ranges = date_ranges
        self.leaderboards = []
        self._already_used_segment_names = []
        self.token = ''
        
    def get(self, token):
        self.token = token
        loop(self._requests())
        return self
        
    async def _requests(self):
        async with ClientSession() as session:
            tasks = []
            for segment in self.segments:
                if not segment.hazardous:
                    for date_range in self.date_ranges:
                        tasks.append(
                            self._get_leaderboard(
                                segment,
                                session,
                                date_range
                            )
                        )
            await asyncio.gather(*tasks)
            
    async def _get_leaderboard(self, segment, session, date_range):
        leaderboard = await segment.get_leaderboard(self.token, session, date_range)
        entries = leaderboard.entries
         
        # if already received any response for particular segment name,
        # update leaderboard entries by new date range...
        if segment.name in self._already_used_segment_names:
            for l in self.leaderboards:
                if l.segment_name == segment.name:
                    leaderboard.entries = l.entries.update(
                        {date_range: entries}
                    )
        # ..., otherwise create first leaderboard
        # for particular segment
        else:
            leaderboard.entries = {
                date_range: entries,
            }
            
            self.leaderboards.append(leaderboard)
            self._already_used_segment_names.append(segment.name)
            
    def pickle(self, activity_id):
        path = os.path.join(
            settings.MEDIA_ROOT,
            'demo_data',
            'leaderboards',
            '{}'.format(activity_id),
         )
        with open(path, 'wb') as f:
            pickle.dump(self.leaderboards, f)
    
class SegmentsPolylines:
    def __init__(self, segments):
        self.segments = segments
        self.polylines = {}
        self.token = ''
        
    def get(self, token):
        self.token = token
        loop(self._requests())
        return self.polylines
        
    async def _get_segment_polyline(self, segment, session):
        polyline = await segment.get_polyline(self.token, session)
        self.polylines.update({
            segment.id: polyline,
        })
               
    async def _requests(self):
        async with ClientSession() as session:
            tasks = []
            for segment in self.segments:
                tasks.append(self._get_segment_polyline(segment, session))
            await asyncio.gather(*tasks)
            
def loop(f):
    l = asyncio.new_event_loop()
    asyncio.set_event_loop(l)
    result = l.run_until_complete(f)
    
#~ def async_get_leaderboards(date_ranges, token, segments):  
  
    #~ leaderboards = []
    #~ already_used_segment_names = []

    #~ async def get_leaderboard(segment, session, date_range):
        #~ request = SegmentLeaderboardRequest(token, segment.id, date_range)
        #~ response = await request.async_get(session)
        #~ entries = response['entries']
        #~ leaderboard = SegmentLeaderboard(segment, entries)
         
        #~ # if already received any response for particular segment name,
        #~ # update leaderboard entries by new date range...
        #~ if segment.name in already_used_segment_names:
            #~ for l in leaderboards:
                #~ if l.segment_name == segment.name:
                    #~ leaderboard.entries = l.entries.update(
                        #~ {date_range: entries}
                    #~ )
        #~ # ..., otherwise create first leaderboard
        #~ # for particular segment
        #~ else:
            #~ leaderboard.entries = {
                #~ date_range: entries,
            #~ }
            
            #~ leaderboards.append(leaderboard)
            #~ already_used_segment_names.append(segment.name)
               
    #~ async def requests(segments):
        #~ async with ClientSession() as session:
            #~ tasks = []
            #~ for segment in segments:
                #~ if not segment.hazardous:
                    #~ for date_range in date_ranges:
                        #~ tasks.append(
                            #~ get_leaderboard(
                                #~ segment,
                                #~ session,
                                #~ date_range
                            #~ )
                        #~ )
            #~ await asyncio.gather(*tasks)
            
    #~ loop(requests(segments=segments))

    #~ return leaderboards

        
#~ def async_get_segments_polylines(segments, token):  
    
    #~ polylines = {}

    #~ async def get_segment_polyline(segment, session):
        #~ polyline = await segment.get_polyline(token, session)
        #~ polylines.update({
            #~ segment.id: polyline,
        #~ })
               
    #~ async def requests(segments):
        #~ async with ClientSession() as session:
            #~ tasks = []
            #~ for segment in segments:
                #~ tasks.append(get_segment_polyline(segment, session))
            #~ await asyncio.gather(*tasks)
            
    #~ loop(requests(segments=segments))
    
    #~ return polylines
    

    
