from django.shortcuts import render

# from .models import Ph, Temperature, Moisture, Color

def index(request):
    ph_data = 0
    temperature_data = 0
    moisture_data = 0
    color_data = 0

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
