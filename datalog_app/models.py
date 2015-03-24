from django.db import models

class Reading(models.Model):
    data = models.TextField()
    meta = models.TextField()

