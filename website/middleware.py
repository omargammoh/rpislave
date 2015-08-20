from django.http import HttpResponseRedirect
from re import compile
from django.conf import settings
from website.templatetags.customfilters import conf
from django.shortcuts import render_to_response
from django.template import RequestContext

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
 
class StandardExceptionMiddleware:
    def process_exception(self, request, exception):
        print "xxxxxxxxxxxxxxxxxxxxxxxxxxx"*100
        #return technical_500_response(request, *sys.exc_info())
        #if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        return None

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware'. If that doesn't work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes 'django.core.context_processors.auth'."
        if conf is None:
            return render_to_response("confsetup.html", {}, context_instance=RequestContext(request))

        #request coming directly from server connected to via rev ssh HTTP_HOST=127.0.0.1:47604
        #request coming from slave itself 127.0.0.1:9001
        if request.META.get('HTTP_HOST', '-').startswith('127.0.0.1'):
            return None
        #request coming directly from server connected to via vpn HTTP_HOST=10.0.0.*
        if request.META.get('HTTP_HOST', '-').startswith('10.0.0'):
            return None
        #request coming from a client through server which is connected to via vpn HTTP_HOST=e.g. 52.24.168.465 (ip of server)
        if request.META.get('HTTP_HOST', '-').startswith(''):
            pass

        if request.user.is_authenticated():
            return None
        if any(m.match(request.path_info.lstrip('/')) for m in EXEMPT_URLS):
            return None

        print ">> LoginRequiredMiddleware: redirecting to login, HTTP_HOST = %s" %request.META.get('HTTP_HOST', '-')
        return HttpResponseRedirect('%s?next=%s&http_host=%s' % (settings.LOGIN_URL, request.path, request.META.get('HTTP_HOST', '-')))



