from django.db import models


class SoilCondition(models.Model):
    id = models.AutoField(primary_key=True)
    ph_value = models.FloatField()
    temperature_value = models.IntegerField()
    moisture_value = models.IntegerField()
    rgb_value = models.IntegerField()
    timestamps = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id + self.ph_value + self.temperature_value + self.moisture_value + self.rgb_value)