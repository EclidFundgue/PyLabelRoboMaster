from typing import List

import cv2

from .label_io import LabelInputOutput
from .verify_points import correctLabelByPoints

# DOTO: import Yolov8Net
# from .yolov8 import Yolov8Net
# net = Yolov8Net()

def relabel(img: cv2.Mat, original_labels: List[LabelInputOutput]) -> List[LabelInputOutput]:
    # return net(img)
    return original_labels

def correctLabels(img: cv2.Mat, labels: List[LabelInputOutput]) -> List[LabelInputOutput]:
    res = []
    for lb in labels:
        kpts = correctLabelByPoints(img, lb.kpts)
        res.append(LabelInputOutput(lb.id, kpts))
    return res