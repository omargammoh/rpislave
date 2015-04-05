from django.contrib import admin
from motion_app.models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

admin.site.register(Event, EventAdmin)
