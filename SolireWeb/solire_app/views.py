from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font
import json
from .helpers import PlantRecommendationFuzzySystem

from .models import SoilCondition

# Initialize the fuzzy system globally or as a singleton
# This avoids re-initializing the system on every request, which can be slow.
fuzzy_system_instance = PlantRecommendationFuzzySystem()

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

def clear_data(request):
    try:
        SoilCondition.objects.all().delete()
        return JsonResponse({
            'success': True,
            'message': 'Data cleared successfully'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def generate_report(request):
    """
    Generate an Excel report from the database.
    """
    try:
        soil_conditions = SoilCondition.objects.all().order_by('-timestamps')
        wb = Workbook()
        ws = wb.active

        # Set header row
        header_row = ['#', 'Temperature (C)', 'Moisture (%)', 'pH', 'Timestamps']
        for col, val in enumerate(header_row, start=1):
            cell = ws.cell(row=1, column=col)
            cell.value = val
            cell.font = Font(bold=True)

        # Set data rows
        for row_idx, sc in enumerate(soil_conditions, start=2):
            ws.cell(row=row_idx, column=1).value = row_idx - 1
            ws.cell(row=row_idx, column=2).value = sc.temperature_value
            ws.cell(row=row_idx, column=3).value = sc.moisture_value
            ws.cell(row=row_idx, column=4).value = sc.ph_value
            ws.cell(row=row_idx, column=5).value = sc.timestamps.strftime('%d-%m-%Y %H:%M:%S')

        # Prepare the file for download
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="soil_conditions_report.xlsx"'
        wb.save(response)

        return response

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def recommend_plant(request):
    if request.method == 'GET':
        # Get parameters from GET request (e.g., /recommend/?ph=6.5&temp=28&humidity=70)
        try:
            ph_value = float(request.GET.get('ph'))
            temp_value = float(request.GET.get('temp'))
            humidity_value = float(request.GET.get('humidity'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid or missing input parameters. Please provide ph, temp, and humidity as numbers.'}, status=400)

        try:
            recommendation_results = fuzzy_system_instance.get_plant_recommendation(
                ph_value, temp_value, humidity_value
            )
            return JsonResponse(recommendation_results)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            # Catch any other unexpected errors from the fuzzy system
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)

    elif request.method == 'POST':
        # Get parameters from POST request (e.g., JSON payload)
        import json
        try:
            data = json.loads(request.body)
            ph_value = float(data.get('ph'))
            temp_value = float(data.get('temp'))
            humidity_value = float(data.get('humidity'))
        except (json.JSONDecodeError, TypeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON or missing input parameters. Please provide ph, temp, and humidity as numbers.'}, status=400)

        try:
            recommendation_results = fuzzy_system_instance.get_plant_recommendation(
                ph_value, temp_value, humidity_value
            )
            return JsonResponse(recommendation_results)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)

    return JsonResponse({'error': 'Only GET and POST requests are supported.'}, status=405)

def recommendation_form(request):
    # A simple view to render a form for input
    return render(request, 'recommendation/recommendation_form.html')