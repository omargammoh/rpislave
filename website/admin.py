from django.contrib import admin
from django.db.models import get_models, get_app

class ModAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

for model in get_models(get_app('website')):
    admin.site.register(model, ModAdmin)
