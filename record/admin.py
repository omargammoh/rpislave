from django.contrib import admin
from record.models import Reading

class ReadingAdmin(admin.ModelAdmin):
    list_display = ('data', 'meta')

admin.site.register(Reading, ReadingAdmin)
