from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('<int:patient_idx>/<int:image_idx>/<int:crop_idx>', patient_detail, name ="patient_detail"),
    path('agree/<int:idx>', agree_tagging, name ="agree_tagging"),
    path('disagree/<int:idx>', disagree_tagging, name ="disagree_tagging"),
    path('interpretation/<int:idx>', write_interpretation, name ="write_interpretation"),
    path('remove_tagging/<int:idx>', remove_tagging, name="remove_tagging"),
    path('remove_interpretation/<int:idx>/', views.remove_interpretation, name='remove_interpretation'),
]
