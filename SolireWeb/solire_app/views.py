from django.shortcuts import render

from .models import Ph, Temperature, Moisture, Color

def index(request):
    ph_data = Ph.objects.all()
    temperature_data = Temperature.objects.all()
    moisture_data = Moisture.objects.all()
    color_data = Color.objects.all()

    return render(
        request,
        'solire_app/index.html',
        {
            'ph_data': ph_data,
            'temperature_data': temperature_data,
            'moisture_data': moisture_data,
            'color_data': color_data,
        },
    )
