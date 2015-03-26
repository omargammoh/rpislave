from django.db import models

class Conf(models.Model):
    data = models.TextField()
    meta = models.TextField()
