from django.conf.urls import patterns, url

from motion_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^get_files/$', views.get_files),
    url(r'^send_usr1/$', views.send_usr1),
    url(r'^send_sigterm/$', views.send_sigterm),
    url(r'^send_sighup/$', views.send_sighup),
    url(r'^recent_events/$', views.recent_events),

)