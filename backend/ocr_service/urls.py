"""
URL configuration for OCR service app
"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def ocr_status(request):
    return Response({'message': 'OCR Service API - Coming Soon'})

app_name = 'ocr_service'

urlpatterns = [
    path('', ocr_status, name='ocr-status'),
]