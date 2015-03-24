from django.contrib import admin
from mng.models import Conf

class ConfAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

admin.site.register(Conf, ConfAdmin)
