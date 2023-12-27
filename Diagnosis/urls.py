from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path("", diagnosis_home, name ='diagnosis_home'),
    path("summary/<int:patient_idx>/<int:image_idx>/<int:crop_idx>", diagnosis_summary, name ="diagnosis_summary"),
    path("tagging/<int:idx>", check_summary, name ="check_summary"),
    path("remove/<int:idx>", remove_patient, name ="remove_patient"),
]