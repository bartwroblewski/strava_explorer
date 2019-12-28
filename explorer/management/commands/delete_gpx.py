from django.core.management.base import BaseCommand

from explorer.models import GPXFile

class Command(BaseCommand):
    '''Remove non-demo GPX files from database and disk'''
    def handle(self, *args, **options):
        files = GPXFile.objects.filter(is_demo=False)
        for f in files:
            # deleting each object individually
            # to enforce model's custom
            # delete method.
            f.delete()
            
