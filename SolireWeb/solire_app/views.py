from django.shortcuts import render
from django.views import generic

from .models import Ph, Temperature, Moisture, Color


class IndexView(generic.ListView):
    template_name = 'solire_app/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        ph_data = Ph.objects.all()
        temperature_data = Temperature.objects.all()
        moisture_data = Moisture.objects.all()
        color_data = Color.objects.all()
        return {
            'ph_data': ph_data,
            'temperature_data': temperature_data,
            'moisture_data': moisture_data,
            'color_data': color_data,
        }

