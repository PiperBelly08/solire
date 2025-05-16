from django.shortcuts import render

from .models import SoilCondition

def index(request):
    return render(
        request,
        'solire_app/index.html',
        {
            'soil_conditions': SoilCondition.objects.all(),
        },
    )
