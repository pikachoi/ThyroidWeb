# dcm_converter/utils.py

import pydicom
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

def convert_dcm_to_image(dcm_file):
    try:
        ds = pydicom.read_file(dcm_file)

        arr = ds.pixel_array

        rescale_slope = ds.RescaleSlope
        rescale_intercept = ds.RescaleIntercept
        window_center = ds.WindowCenter[0]
        window_width = ds.WindowWidth[0]

        scaled_arr = arr * rescale_slope + rescale_intercept

        min_output_value = (2 * window_center - window_width) / 2
        max_output_value = (2 * window_center + window_width) / 2

        scaled_arr = np.clip(scaled_arr, min_output_value, max_output_value)
        scaled_arr = ((scaled_arr - min_output_value) / (max_output_value - min_output_value) * 255).astype('uint8')

        image = Image.fromarray(scaled_arr)
        image_io = BytesIO()
        
        image.save(image_io, format = 'JPEG')

        return image_io
    except Exception as e:
         print(f"Error converting DCM to image: {e}")
         return None
    





