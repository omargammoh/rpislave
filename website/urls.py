from django.conf.urls import patterns, include, url
from django.contrib import admin

import record.views
import send.views
import mng.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', mng.views.home, name='home'),
    url(r'^status/$', mng.views.status),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^record/$', record.views.manage),
    url(r'^record/home$', record.views.home),
    url(r'^send/$', send.views.manage),
)
