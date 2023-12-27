import os, sys, torch, cv2, shutil
import numpy as np

from imutils.paths import list_files

from django.http import HttpResponse
from django.contrib import auth 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.core.paginator import Paginator

from Diagnosis.models import Patient, ImagePath
from Accounts.models import Doctor

from django.conf import settings


# 환자 리스트 페이지

def patient_list(request):
    if request.user.is_authenticated:
        doctorname = request.user.username
        keyword = request.GET.get('keyword')
        search_query = request.GET.get('search')

        if search_query and keyword:
            if keyword == 'index_number':
                try:
                    patient_list = Patient.objects.filter(idx=int(search_query)).order_by("-visit_date")
                except ValueError:
                    patient_list = None
                    return render(request, "PatientList_patient_list.html", context = {"type_error" : "(숫자입력)"})
                    
            elif keyword == 'patient_id':
                patient_list = Patient.objects.filter(patient_name__icontains=search_query).order_by("-visit_date")
            elif keyword == 'user':
                patient_list = Patient.objects.filter(doctor__username=search_query).order_by("-visit_date")
        else:
            patient_list = Patient.objects.all().order_by("-visit_date")

        entry = request.GET.get('entry', '20')  
        entry = int(entry)

        page = request.GET.get('page', 1)

        if patient_list is not None:  # patient_list가 None이 아닐 때에만 페이지네이션 수행
            paginator = Paginator(patient_list, entry)
            page_obj = paginator.get_page(page)
        else:
            page_obj = None

        context = {
            "doctorname": doctorname,
            "patient_list": page_obj,
            "entry": entry,
        }

        return render(request, "PatientList_patient_list.html", context=context)
    else:
        return redirect("login")





def remove_list(request, idx):
    patient = Patient.objects.get(idx=idx)
    image_paths = ImagePath.objects.filter(patient=idx)

    for image_path in image_paths:
        img_path = image_path.img_path.path
        folder_path = os.path.dirname(img_path)
        shutil.rmtree(folder_path)

    # Delete patient folder
    patient_folder = os.path.join(settings.MEDIA_ROOT, str(patient.visit_date.strftime('%Y/%m/%d')), patient.patient_name, str(patient.idx))
    shutil.rmtree(patient_folder)

    patient.delete()

    return redirect("patient_list")





