import os, sys, cv2
import numpy as np

from pathlib import Path
from imutils.paths import list_files

from django.http import HttpResponse
from django.contrib import auth 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Count

from Diagnosis.models import Patient, ImagePath, Crop
from Accounts.models import Doctor
from .models import Tagging, Interpretation

def patient_detail(request, patient_idx, image_idx = 0, crop_idx = 0) :
    if request.user.is_authenticated :# patient = get_object_or_404(Patient ,pk = idx)
        doctor_username     = Doctor.object.get(pk = request.user)

        patient             = Patient.objects.get(idx = patient_idx)
        images              = ImagePath.objects.filter(patient = patient_idx)
        
        image_idx           = images[0].idx if image_idx == 0 else image_idx
        detect_img          = ImagePath.objects.get(idx = image_idx)

        if len(images) == 1 :
            axial_img_path      = ImagePath.objects.get(idx = image_idx)
            sagittal_img_path   = None
        elif ImagePath.objects.get(idx = image_idx).is_axial :
            axial_img_path      = ImagePath.objects.get(idx = image_idx)
            sagittal_img_path   = ImagePath.objects.get(patient = patient_idx, is_axial = False)
        else :
            axial_img_path      = ImagePath.objects.get(patient = patient_idx, is_axial = True)
            sagittal_img_path   = ImagePath.objects.get(idx = image_idx)

        crop_img_paths      = Crop.objects.filter(img_path = image_idx)
        crop_idx            = crop_img_paths[0].idx if crop_idx == 0 else crop_idx
        crop_img            = Crop.objects.get(idx = crop_idx)

        total_tagging       = Tagging.objects.filter(crop_img_path = crop_idx)
        total_agree         = Tagging.objects.filter(crop_img_path = crop_idx, is_agree = True)
        total_disagree      = Tagging.objects.filter(crop_img_path = crop_idx, is_agree = False)
        interpretation      = Interpretation.objects.filter(patient = patient_idx)
        
        context = {
            "doctor_username"       : doctor_username,
            "patient"               : patient,
            "detect_img"            : detect_img,
            "crop_img"              : crop_img,

            "axial_img_path"        : axial_img_path,
            "sagittal_img_path"     : sagittal_img_path,

            "crop_img_paths"        : crop_img_paths,
            "crop_count"            : crop_img_paths.values("img_path").annotate(cnt = Count("img_path"))[0],


            "total_tagging"         : total_tagging,
            "total_agree"           : total_agree.values("crop_img_path").annotate(cnt = Count("is_agree")),
            "total_disagree"        : total_disagree.values("crop_img_path").annotate(cnt = Count("is_agree")),
            "interpretation"        : interpretation,
        }
        
        if Tagging.objects.filter(crop_img_path=crop_idx, doctor=doctor_username).exists():
            context["disable_buttons"] = True
        else:
            context["disable_buttons"] = False

        return render(request, "ResultDetail_patient_detail.html", context = context )
    else :
        return redirect("login")

def agree_tagging(request, idx) :
    tagging = Tagging(
        is_agree        = True,
        comment         = request.POST["body"],
        crop_img_path   = Crop.objects.get(idx = idx),
        doctor          = Doctor.object.get(pk = request.user)
    )
    tagging.save()
    return redirect("patient_detail", Crop.objects.get(idx = idx).img_path.patient.idx , 0, 0)



def disagree_tagging(request, idx) :
    tagging = Tagging(
        is_agree        = False,
        comment         = request.POST["body"],
        crop_img_path   = Crop.objects.get(idx = idx),
        doctor          = Doctor.object.get(pk = request.user)
    )
    tagging.save()
    return redirect("patient_detail", Crop.objects.get(idx = idx).img_path.patient.idx, 0, 0)
    
    


def remove_tagging(request, idx) :
    
    if request.method == 'POST':
        tagging     = Tagging.objects.get(idx = idx)
        patient_idx = tagging.crop_img_path.img_path.patient.idx
        tagging.delete()
        return redirect("patient_detail", patient_idx, 0, 0) 
    else:
        return HttpResponse("error")




def write_interpretation(request, idx) :
    interpretation = Interpretation(
        interpretation  = request.POST["interpretation"],
        patient         = Patient.objects.get(idx = idx)
    )
    interpretation.save()
    return redirect("patient_detail", idx, 0, 0)



def remove_interpretation(request, idx):
    if request.method == 'POST':
        interpretation = Interpretation.objects.get(idx=idx)
        interpretation.delete()
        return redirect('patient_detail', interpretation.patient.idx, 0, 0) 
    else:
        return HttpResponse("error")