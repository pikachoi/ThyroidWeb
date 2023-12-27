from django.urls import path
from .views import *

urlpatterns = [
    path("", patient_list, name ="patient_list"),
    path("remove/<int:idx>", remove_list, name ="remove_list"),

]
