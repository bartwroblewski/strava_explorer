import os

import gpxpy

from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete

from .utils import file_cleanup

class GPXFileQuerySet(models.QuerySet):
    def delete(self):
        for obj in self.all():
            obj.delete()

class GPXFile(models.Model):
    file = models.FileField(upload_to='GPX_files')
    file_name = models.TextField(default='', blank=True)
    uploaded_at = models.TimeField(default=timezone.now)
    is_demo = models.BooleanField(default=False)
    
    objects = GPXFileQuerySet.as_manager()
    
    def decode(self):
        '''Parse GPX file into a list of 
        latitude/longitude coordinates.
        '''
        with open(self.file.path, 'r') as f:
            gpx = gpxpy.parse(f)
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    latlng = point.latitude, point.longitude
                    points.append(latlng)
        return points
        
    def save(self, *args, **kwargs):
        self.file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        '''Delete instance from database and also its
        associated file from disk.
        This method is also enforced when deleting
        entire queryset.
        '''
        try:
            os.remove(self.file.path)
        except FileNotFoundError:
            pass
        super().delete(*args, **kwargs)
        
    def __str__(self):
        if self.is_demo:
            return '(DEMO) {}'.format(self.file_name)
        else:
            return self.file_name

#~ pre_delete.connect(file_cleanup, sender=GPXFile)

class QuotaLeft(models.Model):
    '''Used to track Strava API requests quota left per 15 minutes/day'''
    per_15_minutes = models.IntegerField()
    per_day = models.IntegerField()
    
    def update(self, response):
        limit =  response.headers['X-RateLimit-Limit'].split(',')
        used = response.headers['X-RateLimit-Usage'].split(',')
        self.per_15_minutes = int(limit[0]) - int(used[0])
        self.per_day = int(limit[1]) - int(used[1])    
        self.save()
    
    def save(self, *args, **kwargs):
        '''Always keep only one instance in the database'''
        quotas = QuotaLeft.objects.all()
        quotas.delete()
        self.pk = 1 
        super().save(*args, **kwargs)
        
    def __repr__(self):
        return '\nRequests left per 15 minutes/day: {}/{}'.format(str(self.per_15_minutes), str(self.per_day))
        
        

            

         
