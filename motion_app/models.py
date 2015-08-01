from django.db import models

# Create your models here.

class EventFile(models.Model):
    data = models.TextField()
    meta = models.TextField()