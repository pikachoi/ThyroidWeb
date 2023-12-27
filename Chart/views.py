import os, sys, torch, cv2
import numpy as np

from imutils.paths import list_files

from django.http import HttpResponse
from django.contrib import auth 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.core.paginator import Paginator

from Diagnosis.models import Patient, ImagePath, Crop
from Accounts.models import Doctor
from ResultDetail.models import Tagging

def patient_chart(request) :
    if request.user.is_authenticated :
        doctorname          = request.user.username
        agree_tagging       = Tagging.objects.filter(is_agree = True).count()
        disagree_tagging    = Tagging.objects.filter(is_agree = False).count()
        crops               = Crop.objects.all()
        my_crops            = Crop.objects.filter(img_path__patient__doctor = doctorname)

        if agree_tagging == 0 and disagree_tagging == 0 :
            quantitative_Data = "No Data"
        elif agree_tagging != 0 :
            quantitative_Data = agree_tagging / (agree_tagging + disagree_tagging) * 100
        else :
            quantitative_Data = 0

        k_labels, m_labels, p_labels = [f'C{idx}' for idx in range(1, 6)], [ 'Absent', 'Benign', 'Malignant'], [ 'Absent', 'Negative', 'Positive']
        tk_datas, tm_datas, tp_datas = [0, 0, 0, 0, 0], [0, 0, 0], [0, 0, 0]
        
        for i in crops :
            if i.is_nodule :
                grade = np.argmax(i.classifi_result["K-TIRADS"])
                tk_datas[grade + 1] += 1
                if grade == 0 or grade == 1 :
                    tm_datas[1] += 1
                    tp_datas[1] += 1
                else :
                    tm_datas[2] += 1
                    tp_datas[2] += 1
            else :
                tk_datas[0] += 1
                tm_datas[0] += 1
                tp_datas[0] += 1

        pk_datas, pm_datas, pp_datas = [0, 0, 0, 0, 0], [0, 0, 0], [0, 0, 0]
        for i in my_crops :
            if i.is_nodule :
                grade = np.argmax(i.classifi_result["K-TIRADS"])
                pk_datas[grade + 1] += 1
                if grade == 0 or grade == 1 :
                    pm_datas[1] += 1
                    pp_datas[1] += 1
                else :
                    pm_datas[2] += 1
                    pp_datas[2] += 1
            else :
                pk_datas[0] += 1
                pm_datas[0] += 1
                pp_datas[0] += 1

        

        context = {
            "doctorname"            : doctorname ,
            "quantitative_Data"     : quantitative_Data,
            "agree_tagging"         : agree_tagging,
            "disagree_tagging"      : disagree_tagging,
            "agree_rate"            : (agree_tagging / (agree_tagging + disagree_tagging) * 100) if agree_tagging != 0 else 0 ,
            "disagree_rate"         : (disagree_tagging / (agree_tagging + disagree_tagging) * 100) if disagree_tagging != 0 else 0,
            "crops_count"           : crops.count(),
            "my_crops_count"        : my_crops.count(),

            "k_labels"              : k_labels,
            "m_labels"              : m_labels,
            "p_labels"              : p_labels,
            "tk_datas"              : tk_datas,
            "tm_datas"              : tm_datas,
            "tp_datas"              : tp_datas,
            "pk_datas"              : pk_datas,
            "pm_datas"              : pm_datas,
            "pp_datas"              : pp_datas,

            }
        
        return render(request, "Chart_patient_chart.html", context = context)
    else :
        return redirect("login")
