from django.conf.urls import patterns, url

from camshoot_app import views

urlpatterns = patterns('',
    url(r'^home/$', views.home),
    url(r'^snapshot/$', views.snapshot),
    )