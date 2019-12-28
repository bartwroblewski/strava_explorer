from django.contrib import admin

from .models import GPXFile, QuotaLeft

# Register your models here.
admin.site.register(GPXFile)
admin.site.register(QuotaLeft)
