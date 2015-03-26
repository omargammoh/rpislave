from django.conf.urls import patterns, url

from datalog_app import views

urlpatterns = patterns('',
    url(r'^home/$', views.home),
    )