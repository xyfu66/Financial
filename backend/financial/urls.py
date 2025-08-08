"""
URL configuration for financial app
"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def financial_dashboard(request):
    return Response({'message': 'Financial API - Coming Soon'})

app_name = 'financial'

urlpatterns = [
    path('', financial_dashboard, name='financial-dashboard'),
]