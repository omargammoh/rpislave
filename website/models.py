from django.db import models

class Conf(models.Model):
    data = models.TextField()
    meta = models.TextField()
    mode = "nodelete"

class Log(models.Model):
    data = models.TextField()
    meta = models.TextField()
    mode = "nodelete"

class Error(models.Model):
    data = models.TextField()
    meta = models.TextField()
    mode = "nodelete"