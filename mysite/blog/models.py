from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from taggit.managers import TaggableManager


class Cities_maps(models.Model):
    city_name_client = models.CharField(max_length=250)
    city_name_product = models.CharField(max_length=250)
    class Meta:
        db_table = 'cities'

class Tariff(models.Model):
    start_distance = models.IntegerField()
    end_distance = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.start_distance} - {self.end_distance} км: {self.price} грн"