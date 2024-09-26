import os
from typing import List

import cv2
from ultralytics import YOLO

from ..label_io import LabelInputOutput
from .translator import predict_with_split_windows


class Yolov8Net:
    def __init__(self, path: str):
        self.model = YOLO(path, task='pose')

    def __call__(self, img: cv2.Mat) -> List[LabelInputOutput]:
        h, w, ch = img.shape
        ls = predict_with_split_windows(self.model, img, 544)
        res = []
        for lb in ls:
            idx = lb[0]
            xs = [x / w for x in lb[5::2]]
            ys = [y / h for y in lb[6::2]]
            pts = list(zip(xs, ys))
            res.append(
                LabelInputOutput(idx, pts)
            )
        return res