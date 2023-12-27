import os
import numpy as np

from django import template
from imutils.paths import list_files

register = template.Library()

@register.filter
def detect_nodule_img(image_obj) :
    return os.path.split(image_obj)[0] + os.path.sep + "nodule" + os.path.sep + os.path.split(image_obj)[1]
            
@register.filter
def get_classification(classification_info) :
    if len(classification_info["K-TIRADS"]) == 0 :
        return None
    return f"C{np.argmax(classification_info['K-TIRADS']) + 2}" 

@register.filter
def get_classification_list(classification_info) :
    if len(classification_info["K-TIRADS"]) == 0 :
        return None
    
    res = dict()
    for i in range(len(classification_info["K-TIRADS"])) :
        res[f"C{i + 2}"] = classification_info["K-TIRADS"][i] * 100
    return res.items()

@register.filter
def get_BM(classification_info) :
    if len(classification_info["K-TIRADS"]) == 0 :
        return None
    
    if classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1] > 0.5 :
        return f"B\t(B : {(classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1]) * 100:.3f} %, M : {(classification_info['K-TIRADS'][2] + classification_info['K-TIRADS'][3]) * 100:.3f} % )"
    else :
        return f"M\t(B : {(classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1]) * 100:.3f} %, M : {(classification_info['K-TIRADS'][2] + classification_info['K-TIRADS'][3]) * 100:.3f} % )"

@register.filter
def get_PN(classification_info) :
    if len(classification_info["K-TIRADS"]) == 0 :
        return None
    
    if classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1] > 0.5 :
        return f"N\t(P : {(classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1]) * 100:.3f} %, N : {(classification_info['K-TIRADS'][2] + classification_info['K-TIRADS'][3]) * 100:.3f} % )"
    else :
        return f"P\t(P : {(classification_info['K-TIRADS'][0] + classification_info['K-TIRADS'][1]) * 100:.3f} %, N : {(classification_info['K-TIRADS'][2] + classification_info['K-TIRADS'][3]) * 100:.3f} % )"


