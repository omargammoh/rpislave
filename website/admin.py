from django.contrib import admin
from website.models import Conf, Log, Error

class ConfAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

class LogAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

class ErrorAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

admin.site.register(Conf, ConfAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Error, ErrorAdmin)
