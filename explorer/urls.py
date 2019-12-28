from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'explorer'
urlpatterns = [
    path('', views.index, name='index'),
    path('authorize', views.authorize, name='authorize'),
    path('toggle_demo_mode', views.toggle_demo_mode, name='toggle_demo_mode'),
    path('waiting_screen', views.waiting_screen, name='waiting_screen'),
    path('cache_athlete_activities', views.cache_athlete_activities, name='cache_athlete_activities'),
    path('explorer', views.explorer, name='explorer'),
    path('explorer_data', views.explorer_data, name='explorer_data'),
    path('leaderboards', views.leaderboards, name='leaderboards'),
    path('leaderboards_data', views.leaderboards_data, name='leaderboards_data'),
    path('have_I_been_there', views.have_I_been_there, name='have_I_been_there'),
    path('flush_session', views.flush_session, name='flush_session'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
