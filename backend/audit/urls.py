"""
URL configuration for audit app
"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def audit_list(request):
    return Response({'message': 'Audit API - Coming Soon'})

app_name = 'audit'

urlpatterns = [
    path('', audit_list, name='audit-list'),
]