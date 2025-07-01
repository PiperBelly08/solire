from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json

from .models import SoilCondition

def index(request):
    return render(
        request,
        'solire_app/index.html',
        {
            'soil_conditions': SoilCondition.objects.all(),
        },
    )

@require_http_methods(["POST"])
def insert_data(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)

        # Create new instance
        obj = SoilCondition.objects.create(
            temperature_value=data['temperature_c'],
            moisture_value=data['moisture_percent'],
            ph_value=data['ph_value'],
        )

        return JsonResponse({
            'success': True,
            'message': 'Data inserted successfully',
            'id': obj.id
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def list_data(request):
    try:
        soil_conditions = SoilCondition.objects.all().order_by('-timestamps')
        return JsonResponse({
            'success': True,
            'data': list(soil_conditions.values())
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)