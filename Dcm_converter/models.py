from django.db import models

class ConvertedFile(models.Model):
    dcm_file = models.FileField(upload_to = 'dcm_files/')
    image_file = models.ImageField(upload_to = 'image_files/', blank = True, null = True)