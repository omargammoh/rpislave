from django.conf.urls import patterns, include, url
from django.contrib import admin

import datalog_app.views
import datasend_app.views
import mng.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', mng.views.home, name='home'),
    url(r'^status/$', mng.views.status),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^mng/$', mng.views.manage),

    url(r'^datalog_app/$', datalog_app.views.manage),
    url(r'^datalog_app/home$', datalog_app.views.home),
    url(r'^datasend_app/$', datasend_app.views.manage),
)
