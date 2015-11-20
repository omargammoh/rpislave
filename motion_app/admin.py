from django.contrib import admin
from django.db.models import get_models, get_app

class ModAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'meta')

for model in get_models(get_app('motion_app')):
    admin.site.register(model, ModAdmin)
