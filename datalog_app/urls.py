from django.conf.urls import patterns, url

from datalog_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^recentdata/$', views.recentdata),
    url(r'^highresmcp3008/$', views.highresmcp3008),
    )