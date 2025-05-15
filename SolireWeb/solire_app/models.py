from django.db import models


class Ph(models.Model):
    id = models.AutoField(primary_key=True)
    ph_value = models.FloatField()
    timestamps = models.DateTimeField(auto_now_add=True)


class Temperature(models.Model):
    id = models.AutoField(primary_key=True)
    temperature_value = models.IntegerField()
    timestamps = models.DateTimeField(auto_now_add=True)


class Moisture(models.Model):
    id = models.AutoField(primary_key=True)
    moisture_value = models.IntegerField()
    timestamps = models.DateTimeField(auto_now_add=True)


class Color(models.Model):
    id = models.AutoField(primary_key=True)
    red_value = models.IntegerField()
    green_value = models.IntegerField()
    blue_value = models.IntegerField()
    timestamps = models.DateTimeField(auto_now_add=True)
