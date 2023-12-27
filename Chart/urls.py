from django.urls import path
from .views import *

urlpatterns = [
    path("", patient_chart, name ="patient_chart"),

]
