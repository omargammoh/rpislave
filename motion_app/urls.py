from django.conf.urls import patterns, url

from motion_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^send_signal/$', views.send_signal),
    url(r'^du/$', views.du),
    url(r'^recent_events/$', views.recent_events),
    url(r'^register_event/$', views.register_event),
    url(r'^gantt_data/$', views.gantt_data),
    url(r'^getfile/$', views.getfile)
)


