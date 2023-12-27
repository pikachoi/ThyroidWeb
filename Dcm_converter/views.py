from django.shortcuts import render

# Create your views here.
# dcm_converter/views.py

from django.shortcuts import render, redirect
from .models import ConvertedFile
from .utils import convert_dcm_to_image
# dcm_converter/views.py

import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse

def upload_file(request):
    if request.method == 'POST':
        dcm_file = request.FILES['dcm_file']
        converted_image = convert_dcm_to_image(dcm_file)

        if converted_image:
            # 이미지를 파일로 저장
            converted_file = ConvertedFile(dcm_file=dcm_file)
            converted_file.image_file.save(f"{dcm_file.name.replace('.dcm', '.jpg')}", SimpleUploadedFile(f"{dcm_file.name.replace('.dcm', '.jpg')}", converted_image.getvalue()))
            converted_file.save()

            # 이미지 파일의 경로를 템플릿에 전달
            image_file_path = converted_file.image_file.url
            return render(request, 'Dcm_upload.html', {'image_file_path': image_file_path})

    return render(request, 'Dcm_upload.html')


def upload_image(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']

        # 이미지 파일을 저장
        converted_file = ConvertedFile(image_file=image_file)
        converted_file.save()

        # 이미지 파일의 경로를 JSON 형식으로 반환
        image_url = converted_file.image_file.url
        return JsonResponse({'image_url': image_url})

    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.shortcuts import render
from .models import ConvertedFile

def file_list(request):
    files = ConvertedFile.objects.all()
    return render(request, 'file_list.html', {'files': files})
