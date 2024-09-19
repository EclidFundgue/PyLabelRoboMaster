import os
from typing import Iterable, List, Tuple, Union

import cv2
import pygame

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