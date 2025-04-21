from django.db import models
import datetime


# Create your models here.
class Building(models.Model):
    address = models.CharField(max_length=100)
    def __str__(self):
        return self.name



