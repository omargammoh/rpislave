from django.conf.urls import patterns, url

from btsync_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    )