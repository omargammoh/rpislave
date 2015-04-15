from django.db import models

class Conf(models.Model):
    data = models.TextField()
    meta = models.TextField()

class Log(models.Model):
    data = models.TextField()
    meta = models.TextField()

class Error(models.Model):
    data = models.TextField()
    meta = models.TextField()
