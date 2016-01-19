from django.conf.urls import patterns, include, url
from django.contrib import admin

import website.settings
from website.processing import get_conf

import website.views
import traceback

patterns_tup = ('',
    #website's urls
    url(r'^$', website.views.home, name='home'),
    url(r'^confsetup/$', website.views.confsetup),
    url(r'^set_conf/$', website.views.set_conf),
    url(r'^status/$', website.views.status),
    url(r'^process/$', website.views.appmanage),
    url(r'^cmd/$', website.views.cmd),
    url(r'^test/$', website.views.test),
    url(r'^commits_behind/$', website.views.commits_behind),
    url(r'^rqst/$', website.views.rqst),
    url(r'^blink/$', website.views.blink_led),

    #include admin
    url(r'^admin/', include(admin.site.urls)),
)


#include apps e.g. url(r'^some_app/', include('some_app.urls')),
try:
    appnames = get_conf()['apps'].keys()
except:
    print "> urls: app names could not be loaded from conf"
    appnames = []


for app in appnames:
    try:
        if not (app in website.settings.RPI_APPS):
            raise BaseException('the app %s was not found in the settings.RPI_APPS list' % app )

        toadd = url(r'^%s/' %app, include('%s.urls' %app))
        patterns_tup = patterns_tup + (toadd,)
        print "> included urls from %s" % app
    except:
        toadd = url(r'^%s/' %app, website.views.nourls(traceback.format_exc()))
        patterns_tup = patterns_tup + (toadd,)
        print '> !!could not include urls from the app %s' % (app)


urlpatterns = patterns(*patterns_tup)
