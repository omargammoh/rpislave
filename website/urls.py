from django.conf.urls import patterns, include, url
from django.contrib import admin

import datalog_app.views
import datasend_app.views
import gpio_app.views
import mng.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', mng.views.home, name='home'),
    url(r'^status/$', mng.views.status),
    url(r'^admin/', include(admin.site.urls)),


    url(r'^process/$', mng.views.appmanage),
    url(r'^app-home/$', mng.views.apphome),

    url(r'^gpio_app/pins/$', gpio_app.views.pins),

)
