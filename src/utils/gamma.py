import cv2
import numpy as np


def getGammaTable(gamma: float):
    ''' table[x] = c * x^gamma '''
    table = np.arange(256, dtype=np.float32) # from 0 to 255
    c = np.power(255, 1 - gamma, dtype=np.float32) # Normalize constant
    table = np.power(table, gamma, dtype=np.float32) * c
    table = np.round(table).astype(np.uint8)
    return table

def gammaTransformation(img: cv2.Mat, gamma: float) -> cv2.Mat:
    ''' Use gamma transformation to make image lighter or darker. '''
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    table = getGammaTable(gamma)
    hsv_img[:, :, 2] = table[hsv_img[:, :, 2]] # change light channel in HSV image

    return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)