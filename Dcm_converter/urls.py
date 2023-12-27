# dcm_converter/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('file_list/', views.file_list, name='file_list'),
]
