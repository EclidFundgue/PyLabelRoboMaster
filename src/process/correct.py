import os
from typing import List

import cv2

from ..resources_loader import ConfigLoader
from ..utils.constants import ROOT_PATH
from .label_io import LabelInputOutput
from .verify_points import correctLabelByPoints

# Load network by config
__loader = ConfigLoader()
if __loader['load_network']:
    from .yolov8 import Yolov8Net
    net = Yolov8Net(os.path.join(ROOT_PATH, __loader['model_path']))


def relabel(img: cv2.Mat, original_labels: List[LabelInputOutput]) -> List[LabelInputOutput]:
    if __loader['load_network']:
        return net(img)
    return original_labels

def correctLabels(img: cv2.Mat, labels: List[LabelInputOutput]) -> List[LabelInputOutput]:
    res = []
    for lb in labels:
        kpts = correctLabelByPoints(img, lb.kpts)
        res.append(LabelInputOutput(lb.id, kpts))
    return res