from django.conf.urls import patterns, url

from gpio_app import views

urlpatterns = patterns('',
    url(r'^home/$', views.home),
    url(r'^pins/$', views.pins),
    )