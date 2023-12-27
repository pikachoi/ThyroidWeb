from django.db import models

from Accounts.models import Doctor
from Diagnosis.models import Patient, Crop


class Tagging(models.Model) :
    idx             = models.AutoField(primary_key = True)
    crop_img_path   = models.ForeignKey(Crop, on_delete = models.CASCADE, db_column="crop_img_path", default = None)
    doctor          = models.ForeignKey(Doctor, on_delete = models.CASCADE, db_column = "doctor", default = None)
    write_date      = models.DateTimeField(verbose_name = "write_date", auto_now = True)
    is_agree        = models.BooleanField(default = False)
    comment         = models.CharField(max_length = 1024, default = None)
    
class Interpretation(models.Model) :
    idx             = models.AutoField(primary_key = True) 
    patient         = models.ForeignKey(Patient, on_delete = models.CASCADE, db_column = "patient")
    write_date      = models.DateTimeField(verbose_name = "write_date", auto_now = True)
    interpretation  = models.CharField(max_length = 1024)