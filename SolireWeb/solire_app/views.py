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
    
from openpyxl import Workbook
from openpyxl.styles import Font

from django.http import HttpResponse

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