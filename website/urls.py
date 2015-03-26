from django.conf.urls import patterns, include, url
from django.contrib import admin
import website.settings

import website.views


patterns_tup = ('',
    #website's urls
    url(r'^$', website.views.home, name='home'),
    url(r'^status/$', website.views.status),
    url(r'^process/$', website.views.appmanage),
    url(r'^app-home/$', website.views.apphome),

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
        toadd = url(r'^%s/' %app, website.views.nourls)
        patterns_tup = patterns_tup + (toadd,)
        print '!!could not include urls from the app %s' % (app)


urlpatterns = patterns(*patterns_tup)
