"""
URL configuration for notifications app
"""
from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def notification_list(request):
    return Response({'message': 'Notifications API - Coming Soon'})

app_name = 'notifications'

urlpatterns = [
    path('', notification_list, name='notification-list'),
]