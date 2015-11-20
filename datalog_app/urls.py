from django.conf.urls import patterns, url

from datalog_app import views

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^recentdata/$', views.recentdata),
    url(r'^highresmcp3008/$', views.highresmcp3008),
    url(r'^highchart/$', views.highchart),
    url(r'^_getdata/$', views._getdata),
    url(r'^_getdata_transformed/$', views._getdata_transformed),
    url(r'^_highchart/$', views._highchart),
    )