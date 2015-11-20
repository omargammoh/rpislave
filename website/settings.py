"""
Django settings for rpislave project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import traceback
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    SECRET_KEY_PATH = os.path.join(BASE_DIR, "SECRET_KEY")
    #if file exists
    if os.path.isfile(SECRET_KEY_PATH):
        #read secret
        f = file(SECRET_KEY_PATH,'r')
        SECRET_KEY = f.read().strip()
        f.close()
        print "Loaded SECRET succesfuly"
    #else
    else:
        #generate secret
        from django.utils.crypto import get_random_string
        SECRET_KEY = get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
        #save it to file
        f = file(SECRET_KEY_PATH,'w')
        f.write(SECRET_KEY)
        f.close()
        print "Created SECRET succesfuly"
except:
    print '!!SECRET is not secret!! '* 100
    print traceback.format_exc()
    SECRET_KEY = 'ewowx!+2a(frgtz4_elhp6vx+m*hp5ox7$6$b!-y7=otu*2h%l'



# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

TEMPLATE_DEBUG = False



# Application definition

# List here all available apps
RPI_APPS = (
    'datalog_app',
    'gpio_app',
    'motion_app',
    'camshoot_app',
)

# List here all processes that are in website.proc that needed to be started at startup
RPI_PROC = ('btsync',
            'clear',
            'datasend',
            'status',
            'rebooter',)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website',
) + RPI_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.LoginRequiredMiddleware',
    'website.middleware.StandardExceptionMiddleware',
)

LOGIN_URL = "/admin/login/"

ROOT_URLCONF = 'website.urls'

WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

#oga
STATIC_ROOT = '/home/pi/static'

#oga
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

#oga
import os
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\','/'),)

#oga
CONF_LABEL = 'example' #make sure this conf is in the database in the table mng_conf

#this enables accessing the request object in the template
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request'
    )

#todo: this excempt url is just for debug, remove it later
LOGIN_EXEMPT_URLS = ('rqst')

BASE_URL = "http://rpi-master.com/api/slave/?"

