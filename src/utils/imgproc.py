__all__ = [
    'makeFolder',
    'getLabelPath',
    'getImageFiles',
    'getPairedPath',
    'sortedPoints',
    'surface2mat',
    'mat2surface',
    'gammaTransformation',
    'relabel',
    'correctLabels',
]

import os
from typing import Iterable, List, Tuple, Union

import cv2
import numpy as np
import pygame

from .. import pygame_gui as ui
from . import lbformat as fmt

# Binary threshold value
_THRESH = 180

# image file extensions
__image_exts = [
    '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif', '.svg', '.webp'
]

def makeFolder(path: str) -> None:
    ''' Check if this folder exists, ohterwize build recursively. '''
    head, tail = os.path.split(path)
    if head and not os.path.exists(head):
        makeFolder(head)
    if not os.path.exists(path):
        os.mkdir(path)

def getLabelPath(img_file: str, label_folder) -> str:
    n = os.path.splitext(img_file)[0]
    label_file = n + '.txt'
    return os.path.join(label_folder, label_file)

def getImageFiles(img_folder: str) -> Iterable[str]:
    ''' Get all image files in the folder. '''
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
        ui.logger.warning(f'Folder {img_folder} does not exist.')
    return (f for f in os.listdir(img_folder) if os.path.splitext(f)[1].lower() in __image_exts)

def getPairedPath(img_folder: str, label_folder: str) -> List[Tuple[str, Union[str, None]]]:
    """
    get (image, label) pair

    Returns:
        List[Tuple[iamge_path, label_path]]

    `label_path` may not exists
    """

    res = []
    def is_image(f: str):
        name, ext = os.path.splitext(f)
        return ext.lower() in __image_exts
    for im_file in filter(is_image, os.listdir(img_folder)):
        im_path = os.path.join(img_folder, im_file)

        name, ext = os.path.splitext(im_file)
        label_file = name + '.txt'
        lb_path = os.path.join(label_folder, label_file)

        if os.path.exists(lb_path):
            res.append([im_path, lb_path])
        else:
            res.append([im_path, None])

    return res

def sortedPoints(pts: List[Tuple]) -> List[Tuple]:
    ''' sorted by: lt, lb, rb, rt '''
    left2right = sorted(pts, key=lambda p: p[0])

    if left2right[0][1] < left2right[1][1]: # p0.y < p1.y:
        pl = [left2right[0], left2right[1]]
    else:
        pl = [left2right[1], left2right[0]]

    if left2right[2][1] > left2right[3][1]: # p2.y > p3.y:
        pr = [left2right[2], left2right[3]]
    else:
        pr = [left2right[3], left2right[2]]

    return [pl[0], pl[1], pr[0], pr[1]]

def surface2mat(surf: pygame.Surface) -> cv2.Mat:
    np_img = pygame.surfarray.array3d(surf)
    np_img = np_img.transpose(1, 0, 2) # [column, row, channel] -> [row, column, channel]
    return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

def mat2surface(mat: cv2.Mat) -> pygame.Surface:
    cv_rgb = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    return pygame.image.fromstring(
        cv_rgb.data.tobytes(), mat.shape[1::-1], 'RGB'
    )

def _getGammaTable(gamma: float):
    ''' table[x] = c * x^gamma '''
    table = np.arange(256, dtype=np.float32) # from 0 to 255
    c = np.power(255, 1 - gamma, dtype=np.float32) # Normalize constant
    table = np.power(table, gamma, dtype=np.float32) * c
    table = np.round(table).astype(np.uint8)
    return table

def gammaTransformation(img: cv2.Mat, gamma: float) -> cv2.Mat:
    ''' Use gamma transformation to make image lighter or darker. '''
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    table = _getGammaTable(gamma)
    hsv_img[:, :, 2] = table[hsv_img[:, :, 2]] # change light channel in HSV image

    return cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)


def _getCnts(img: cv2.Mat) -> List[Tuple[int, int]]:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, _THRESH, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return cnts

def _distance(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return dx * dx + dy * dy

def _verifyPoint(
        pt: Tuple[float, float],
        cnts: List[Tuple[int, int]]) -> Tuple[float, float]:
    min_dis = 1e6
    cnt_id = -1
    for i, cnt in enumerate(cnts):
        res = abs(cv2.pointPolygonTest(cnt, pt, True))
        if res < 20 and res < min_dis:
            min_dis = res
            cnt_id = i

    # Do not correct if no suitable contour found
    if cnt_id == -1:
        return pt

    rect = cv2.RotatedRect(*cv2.minAreaRect(cnts[cnt_id]))
    # sort by y
    pts = list(sorted(rect.points(), key=lambda x : x[1]))
    light_p1 = (pts[0] + pts[1]) / 2
    light_p2 = (pts[2] + pts[3]) / 2
    if _distance(light_p1, pt) < _distance(light_p2, pt):
        return list(light_p1)
    else:
        return list(light_p2)

def _correctLabelByPoints(img: cv2.Mat, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    cnts = _getCnts(img)
    # Do not correct if no contour found
    if not cnts:
        return points

    h, w, ch = img.shape
    verified_points = []
    for i in range(4):
        x, y = points[i]
        x, y = _verifyPoint((x * w, y * h), cnts)
        verified_points.append((x / w, y / h))

    return verified_points

def relabel(img: cv2.Mat, original_labels: List[fmt.ArmorLabelIO]) -> List[fmt.ArmorLabelIO]:
    return original_labels

def correctLabels(img: cv2.Mat, labels: List[fmt.ArmorLabelIO]) -> List[fmt.ArmorLabelIO]:
    res = []
    for lb in labels:
        kpts = _correctLabelByPoints(img, lb.kpts)
        res.append(fmt.ArmorLabelIO(lb.cls_id, kpts))
    return res