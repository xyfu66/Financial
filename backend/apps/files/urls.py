"""
URL configuration for files app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileUploadView, OCRProcessView, FileDownloadView

app_name = 'files'

urlpatterns = [
    # File upload endpoint
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    
    # OCR processing endpoint
    path('ocr/process/', OCRProcessView.as_view(), name='ocr-process'),
    
    # File download endpoint
    path('download/<str:file_id>/', FileDownloadView.as_view(), name='file-download'),
]