from django.conf.urls import patterns, url

from datalog_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^highresmcp3008/$', views.highresmcp3008),
    url(r'^highchart/$', views.highchart),
    url(r'^getdata_transformed/$', views.getdata_transformed),
    )