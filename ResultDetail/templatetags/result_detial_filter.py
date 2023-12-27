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
def get_spec(classification_info, spec) :
    res = dict()
    if spec == 'BM' :
        bm = classification_info['K-TIRADS']
        res['B'] = f"{(bm[0] + bm[1]) * 100:.3f}"
        res['M'] = f"{(bm[2] + bm[3]) * 100:.3f}"
        return res.items()
    
    elif spec == 'PN' :
        pn = classification_info['K-TIRADS']
        res['P'] = f"{(pn[0] + pn[1]) * 100:.3f}"
        res['N'] = f"{(pn[2] + pn[3]) * 100:.3f}"
        return res.items()
    
    elif spec == "ECHO" :
        echo = classification_info['echogenicity']
        res['Hypoechogenicity'] = f"{echo[0] * 100:.3f}"
        res['Isoechogenicity'] = f"{echo[1] * 100:.3f}"
        return res.items()
    
    elif spec == "MARGIN" :
        margin = classification_info['margin'][0]
        res['Ill-defined'] = f"{margin[0] * 100:.3f}"
        res['Smooth'] = f"{margin[1] * 100:.3f}"
        res['Spiculated'] = f"{margin[2] * 100:.3f}"
        return res.items()

    elif spec == "ECHOGENIC_FOCI" :
        echogenic_foci = classification_info['echogenic_foci']
        res['Absent'] = f"{echogenic_foci[0] * 100:.3f}"
        res['Punctate_echogenic_foci'] = f"{echogenic_foci[1] * 100:.3f}"
        res['Macrocalcifications'] = f"{echogenic_foci[2] * 100:.3f}"
        return res.items()

    elif spec == "ORIENTATION" :
        orientation = classification_info['orientation']
        res['Parallel'] = f"{orientation[0] * 100:.3f}"
        res['Nonparallel'] = f"{(1 - orientation[0]) * 100:.3f}"
        return res.items()
    

    elif spec == "SHAPE" :
        shape = classification_info['shape']
        res['Round_to_oval'] = f"{shape[0] * 100:.3f}"
        res['Irregular'] = f"{shape[1] * 100:.3f}"
        return res.items()

    elif spec == "COMPOSITION" :
        composition  = classification_info['composition'][0]
        res['Solid'] = f"{composition[0] * 100:.3f}"
        res['Predominantly_Solid'] = f"{composition[1] * 100:.3f}"
        res['Benign_Cystic'] = f"{composition[2] * 100:.3f}"
        res['Colloid'] = f"{composition[3] * 100:.3f}"
        res['Spongiform'] = f"{composition[4] * 100:.3f}"
        return res.items()


    elif spec == "GRADE" :
        grade  = classification_info['K-TIRADS']
        res['C2'] = f"{grade[0] * 100:.3f}"
        res['C3'] = f"{grade[1] * 100:.3f}"
        res['C4'] = f"{grade[2] * 100:.3f}"
        res['C5'] = f"{grade[3] * 100:.3f}"
        return res.items()

@register.filter
def get_max_spec(classification_info, spec) :
    
    if spec == 'BM' :
        bm = classification_info['K-TIRADS']
        if (bm[0] + bm[1]) > (bm[2] + bm[3]) :
            return 'B'
        else :
            return 'M'
        
    elif spec == 'PN' :
        pn = classification_info['K-TIRADS']
        if (pn[0] + pn[1]) > (pn[2] + pn[3]) :
            return 'P'
        else :
            return 'N'
    


    elif spec == "ECHO" :
        echo = classification_info['echogenicity']
        max_echo = np.argmax(echo)
        if max_echo == 0 :
            return 'Hypoechogenicity'
        else :
            return 'Isoechogenicity'
        

    
    elif spec == "MARGIN" :
        margin = classification_info['margin'][0]
        max_margin = np.argmax(margin)
        if max_margin == 0 :
            return 'Ill-defined'
        elif max_margin == 1 :
            return 'Smooth'
        else :
            return 'Spiculated'


    elif spec == "ECHOGENIC_FOCI" :
        echogenic_foci = classification_info['echogenic_foci']
        max_echogenic_foci = np.argmax(echogenic_foci)
        print("asd:", max_echogenic_foci)
        if max_echogenic_foci == 0 :
            return 'Absent'
        elif max_echogenic_foci == 1 :
            return 'Punctate_echogenic_foci'
        else :
            return 'Macrocalcifications'



    elif spec == "ORIENTATION" :
        orientation = classification_info['orientation']
        if orientation[0] > 0.5 :
            return 'Parallel'
        else :
            return 'Nonparallel'



    elif spec == "SHAPE" :
        shape = classification_info['shape']
        if shape[0] > shape[1] :
            return 'Round_to_oval'
        else :
            return 'Irregular'
        


    elif spec == "COMPOSITION" :
        composition  = classification_info['composition'][0]
        max_composition = np.argmax(composition)
        print(max_composition)
        if max_composition == 0 :
            return 'Solid'
        elif max_composition == 1 :
            return 'Predominantly_Solid'
        elif max_composition == 2 :
            return 'Benign_Cystic'
        elif max_composition == 3 :
            return 'Colloid'
        else :
            return 'Spongiform'
    

        
    elif spec == "GRADE" :
        grade  = classification_info['K-TIRADS']
        max_grade = np.argmax(grade)
        if max_grade == 0 :
            return 'C2'
        elif max_grade == 1 :
            return 'C3'
        elif max_grade == 2:
            return 'C4'
        else :
            return 'C5'

        