from django.conf.urls import patterns, url

from motion_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    )