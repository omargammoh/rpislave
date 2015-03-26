from django.conf.urls import patterns, include, url
from django.contrib import admin
import website.settings

import mng.views


patterns_tup = ('',
    #mng app urls
    url(r'^$', mng.views.home, name='home'),
    url(r'^status/$', mng.views.status),
    url(r'^process/$', mng.views.appmanage),
    url(r'^app-home/$', mng.views.apphome),

    #include admin
    url(r'^admin/', include(admin.site.urls)),
)



#include apps e.g. url(r'^some_app/', include('some_app.urls')),
for app in website.settings.RPI_APPS:
    try:
        toadd = url(r'^%s/' %app, include('%s.urls' %app))
        patterns_tup = patterns_tup + (toadd,)
        print "added %s" % app
    except:
        print '!!could not include urls from the app %s' % (app)


urlpatterns = patterns(*patterns_tup)
