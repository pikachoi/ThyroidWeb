import os, sys, torch, cv2, shutil
import numpy as np

from pathlib import Path
from imutils.paths import list_files

from django.shortcuts import render, redirect
from django.db.models import Count

from Diagnosis.models import Patient, ImagePath, Crop
from Accounts.models import Doctor

from django.views.decorators.csrf import csrf_exempt
import subprocess
import base64

import time


AI_mode = False

if AI_mode :
    print("\n검출 모델 로드 중...\n")
    from tensorflow.keras.models import load_model

    sys.path.append(f"{Path.cwd()}{os.path.sep}yolov5")

    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[0]  # YOLOv5 root directory

    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))  # add ROOT to PATH
    ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

    from models.common import DetectMultiBackend
    from utils.dataloaders import  LoadImages
    from utils.general import (LOGGER, Profile,  check_img_size,  check_requirements, cv2, increment_path, non_max_suppression, scale_boxes)
    from utils.plots import Annotator, colors, save_one_box
    from utils.torch_utils import select_device, smart_inference_mode
    from scipy.ndimage import median_filter
    from PIL import Image

    check_requirements(exclude=('tensorboard', 'thop'))
    device = select_device('')
    detect_model = DetectMultiBackend(weights = "media/AI_model/best.pt", device=device)

    @smart_inference_mode()
    def yolov5_detect(
            project,
            source,       
            model           = detect_model,
            imgsz           = (640, 640), 
            conf_thres      = 0.25, 
            iou_thres       = 0.45, 
            max_det         = 10,
            save_crop       = True, 
            classes         = 0,
            name            = "nodule", 
            line_thickness  = 2, 
            hide_labels     = True,  
            hide_conf       = True,
            view_img=True,
            use_extend_crop=True
        ) :
        source = str(source)
        save_img = not source.endswith('.txt')  # save inference images
        
        # Directories
        save_dir = increment_path(Path(project) / name, exist_ok=False)  # increment run

        # Load model
        stride, names, pt = model.stride, model.names, model.pt
        imgsz = check_img_size(imgsz, s=stride)  # check image size

        # Dataloader
        bs = 1  # batch_size
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=1)

        # Run inference
        model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
        seen, dt = 0,  (Profile(), Profile(), Profile())
        for path, im, im0s, vid_cap, s in dataset:
            with dt[0]:
                im = torch.from_numpy(im).to(model.device)
                im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
                im /= 255  # 0 - 255 to 0.0 - 1.0
                if len(im.shape) == 3:
                    im = im[None]  # expand for batch dim

            # Inference
            with dt[1]:
                pred = model(im)

            # NMS
            with dt[2]:
                pred = non_max_suppression(pred, conf_thres, iou_thres, classes, max_det=max_det)

            # Process predictions
            for det in pred :  # per image
                seen += 1
                
                p, im0 = path, im0s.copy()

                p = Path(p)  # to Path
                save_path = str(save_dir / p.name)  # im.jpg
                s += '%gx%g ' % im.shape[2:]  # print string
                
                imc = im0.copy()
                annotator = Annotator(im0, line_width=line_thickness, example=str(names))

                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, 5].unique():
                        n = (det[:, 5] == c).sum()  # detections per class
                        s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    # Write results
                    for *xyxy, conf, cls in reversed(det):

                        if save_img or save_crop :  # Add bbox to image
                            c = int(cls)  # integer class
                            label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                            annotator.box_label(xyxy, label, color=colors(c, True))
                        
                            # original crop image save
                            save_one_box(xyxy, imc, file=save_dir / 'crops' / f'{p.stem}_crop.jpg', BGR=True)

                            # extend crop image save
                            xyxy[0] -= 30  # x_min
                            xyxy[1] -= 30  # y_min
                            xyxy[2] += 30  # x_max
                            xyxy[3] += 30  # y_max

                            xyxy[0] = max(xyxy[0], 0)
                            xyxy[1] = max(xyxy[1], 0)
                            xyxy[2] = min(xyxy[2], im0.shape[1])
                            xyxy[3] = min(xyxy[3], im0.shape[0])
                    
                            if save_crop:
                                save_one_box(xyxy, imc, file=save_dir / 'extend_crops' / f'{p.stem}_extend_crop.jpg', BGR=True)

                # Stream results
                im0 = annotator.result()
                
                # Save results (image with detections)
                if save_img:
                    cv2.imwrite(save_path, im0)
                    
            # Print time (inference-only)
            LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")

        # Print results 출력 로그 없어도 됨
        t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
        LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)


    # extend_crop / 224 / CLAHE - > 발테 전처리 o
    def apply_composition(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_image = clahe.apply(gray)
        clahe_image = cv2.cvtColor(clahe_image, cv2.COLOR_GRAY2BGR)

        return clahe_image
    

    # extend crop / 224 / COLOR_RGB2GRAY, meian_filter, 다시 COLOR_GRAY2RGB / 정규화 -> 발테 전처리 적용 o
    def apply_margin(image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) 
        filtered_im = median_filter(gray, 5) 
        filtered_im_rgb = cv2.cvtColor(filtered_im, cv2.COLOR_GRAY2RGB)
        filter_image = filtered_im_rgb / 255

        return filter_image


    # # echogenicity / orientation - ori crop image / 299 / padding  -> 발테 전처리 적용 o
    def apply_orientation_echogenicity(image, target_width, target_height, padding_color=(0, 0, 0)):
        ratio = min(target_width / image.width, target_height / image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        padding_image = Image.new("RGB", (target_width, target_height), padding_color)
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        padding_image.paste(image, (x_offset, y_offset))

        return padding_image


    def calssci_spec_func(image_obj):
            start_time = time.time()

            ori_crop_img = list(list_files(f"{os.path.split(image_obj.img_path.path)[0]}/nodule/crops"))
            extend_crop_img = list(list_files(f"{os.path.split(image_obj.img_path.path)[0]}/nodule/extend_crops"))

            if len(ori_crop_img) == 0 or len(extend_crop_img) == 0:
                crop_raw = Crop(
                    img_path                = ImagePath.objects.get(img_path = image_obj.img_path),
                    crop_img_path           = ""
                )
                crop_raw.save()

            else :
                for i in ori_crop_img:
                    crop_img_224 = cv2.resize(cv2.imread(i), (224, 224))
                    crop_img_299 = cv2.resize(cv2.imread(i), (299, 299))
                    crop_img_array = np.array(crop_img_299)
                    cropped_echogenicity_orientation_img = apply_orientation_echogenicity(Image.fromarray(crop_img_array), 299, 299)
                    crop_result = {
                        "K-TIRADS": classification_model.predict(np.expand_dims(crop_img_299 / 255.0, axis=0)).tolist()[0],
                        "echogenicity": echogenicity_model.predict(np.expand_dims(np.array(cropped_echogenicity_orientation_img) / 255.0, axis=0)).tolist()[0],
                        "margin": [],
                        "echogenic_foci": echogenic_foci_model.predict(np.expand_dims(crop_img_224 / 255.0, axis=0)).tolist()[0],  # 약 3초 원래 정규화 없음
                        "orientation": orientation_model.predict(np.expand_dims(np.array(cropped_echogenicity_orientation_img) / 255.0, axis=0)).tolist()[0],
                        "shape": shape_model.predict(np.expand_dims(crop_img_224 / 255.0, axis=0)).tolist()[0],
                        "composition": [],
                    }

                    for j in extend_crop_img:
                        crop_img_extend = cv2.resize(cv2.imread(j), (224, 224))
                        crop_img_composition = apply_composition(crop_img_extend)
                        crop_img_margin = apply_margin(crop_img_extend)
                        print('margin')
                        margin_value = margin_model.predict(np.expand_dims(crop_img_margin, axis=0)).tolist()[0]
                        print('composition')
                        composition_value = composition_model.predict(np.expand_dims(crop_img_composition / 255.0, axis=0)).tolist()[0]  # 약 2초 원래 정규화 없음
                        crop_result["margin"].append(margin_value)
                        crop_result["composition"].append(composition_value)

                    crop_raw = Crop(
                        img_path=image_obj,
                        crop_img_path=i.split(f"media{os.path.sep}")[-1],
                        is_nodule=True,
                        classifi_result=crop_result
                    )
                    crop_raw.save()

                    end_time = time.time()
                    print("-------------------------------------- 전체 함수 실행 시간: ", end_time - start_time)


    classification_model = load_model("media/AI_model/densenet201.0.87-0.76.h5")
    echogenicity_model = load_model("media/AI_model/Refactoring/Echogenicity/Echogenicity_299.h5")
    margin_model = load_model("media/AI_model/Refactoring/Margin/Margin_224.h5")
    echogenic_foci_model = load_model("media/AI_model/Refactoring/Echogenic_foci/Echogenic_foci_224.h5")
    orientation_model = load_model("media/AI_model/Refactoring/Orientation/Orientation_299.h5")
    shape_model = load_model("media/AI_model/Refactoring/Shape/Shape_224.h5")
    composition_model = load_model("media/AI_model/Refactoring/Composition/Composition_224.h5")


    print("\n모델 첫번째 분류 수행중...\n")

    dummy_image_224 = np.expand_dims(np.zeros((224, 224, 3), dtype = np.uint8), axis = 0)
    dummy_image_299 = np.expand_dims(np.zeros((299, 299, 3), dtype = np.uint8), axis = 0)

    
    print('classification')
    classification_model.predict(dummy_image_299 / 255.0)
    print('echogenicity_model')
    echogenicity_model.predict(dummy_image_299 / 255.0 )
    print('margin_model')
    margin_model.predict(dummy_image_224 / 255.0)
    print('echogenic_foci_model')
    echogenic_foci_model.predict(dummy_image_224 / 255.0)
    print('orientation_model')
    orientation_model.predict(dummy_image_299 / 255.0)
    print('shape_model')
    shape_model.predict(dummy_image_224 / 255.0)
    print('composition_model')
    composition_model.predict(dummy_image_224/ 255.0)
    

from django.views.decorators.cache import never_cache
# 판독 화면 접근시
@csrf_exempt
@never_cache
def diagnosis_home(request):
    if request.user.is_authenticated:
        need_summary = Patient.objects.filter(is_summary=True, doctor=request.user)

        context = {
            "need_summary": need_summary,
        }

        if len(need_summary) >= 1:
            return redirect("diagnosis_summary",
                            patient_idx=need_summary[0].idx,
                            image_idx=0,
                            crop_idx=0
                            )
        
        elif request.method == "POST":
            patient_obj = Patient(
                doctor=request.user,  # 기존: Doctor.objects.get(pk=request.user.pk)
                patient_name=request.POST["patient_id"],
            )
            patient_obj.save()

            image_obj = ImagePath(
                patient=patient_obj,
                
                img_path=request.FILES["imgfile"]
            )
            image_obj.save()
            print("---------------------------------------------------------------------------")
            print(type(image_obj.img_path.path))
            print(image_obj.img_path.path)
            print("---------------------------------------------------------------------------")
            yolov5_detect(source=image_obj.img_path.path, project=os.path.split(image_obj.img_path.path)[0])
            calssci_spec_func(image_obj)

            if "imgfile2" in request.FILES: # 기존: if len(request.FILES) >= 2 :
                image_obj_sagittal = ImagePath(
                    patient=patient_obj, # 기존: Patient.objects.get(pk=patient_obj.idx),
                    img_path=request.FILES["imgfile2"], 
                    is_axial=False
                )

                image_obj_sagittal.save()
                yolov5_detect(source=image_obj_sagittal.img_path.path, project=os.path.split(image_obj_sagittal.img_path.path)[0])
                calssci_spec_func(image_obj_sagittal)

            return redirect("diagnosis_summary",
                            patient_idx=patient_obj.idx,
                            image_idx=image_obj.idx,
                            crop_idx=0,
                            )
        else:
            return render(request, "Diagnosis_main.html", context=context)
    else:
        return redirect("login")
    

# 요약 페이지
def diagnosis_summary(request, patient_idx, image_idx = 0, crop_idx = 0) :
    if request.user.is_authenticated :
        doctor_username     = Doctor.objects.get(pk = request.user)
        need_summary        = Patient.objects.filter(is_summary = True, doctor = request.user)
        
        if len(need_summary) == 0 :
            return redirect("diagnosis_home")
        
        patient                 = Patient.objects.get(idx = patient_idx)
        images                  = ImagePath.objects.filter(patient = patient_idx)
        
        image_idx               = images[0].idx if image_idx == 0 else image_idx
        detect_img              = ImagePath.objects.get(idx = image_idx)

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

        context = {
                "doctor_username"       : doctor_username,
                "need_summary"          : need_summary,
                "patient"               : patient,
                "detect_img"            : detect_img,
                "crop_img"              : crop_img,

                "axial_img_path"        : axial_img_path,
                "sagittal_img_path"     : sagittal_img_path,

                "crop_img_paths"        : crop_img_paths,
                "crop_count"            : crop_img_paths.values("img_path").annotate(cnt = Count("img_path"))[0],
                }
                
        return render(request, "Diagnosis_summary.html", context = context)
    else :
        return redirect("login")
    
    
def check_summary(request, idx) :
    Patient.objects.filter(idx = idx).update(is_summary = False)
    return redirect("patient_detail", idx, 0, 0)


def remove_patient(request, idx) :
    patient = Patient.objects.get(idx = idx)
    image   = ImagePath.objects.filter(patient = idx)
    for i in image :
        shutil.rmtree(os.path.split(i.img_path.url)[0][1:])
    patient.delete()
    return redirect("diagnosis_home")