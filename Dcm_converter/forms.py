from django import forms

class ImageUploadForm(forms.Form):
    dcm_file = forms.FileField(label='Upload DCM File', required=True, accept=".dcm")
