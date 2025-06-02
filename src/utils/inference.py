from typing import List, Tuple

import cv2
import numpy as np

from .lbformat import ArmorLabelIO


class PoseModel:
    def __init__(self,
        model_path: str,
        img_size: Tuple[int, int] = (640, 640),
        num_classes: int = 16,
        num_keypoints: int = 4, 
        confidence_thresh: float = 0.2,
        nms_thresh: float = 0.2
    ):
        self.img_size = img_size
        self.num_classes = num_classes
        self.num_keypoints = num_keypoints
        self.confidence_thresh = confidence_thresh
        self.nms_thresh = nms_thresh

        self.net = cv2.dnn.readNetFromONNX(model_path)
        self.letterbox_scale = 1.0

    def inference(self, img: np.ndarray) -> List[ArmorLabelIO]:
        letterbox_img = self._letterbox(img)

        blob = self._blob_from_image(letterbox_img)
        self.net.setInput(blob)
        output_buffer = self.net.forward()

        class_ids, class_scores, boxes, objects_keypoints = self._read_from_output_buffer(output_buffer)

        indices = cv2.dnn.NMSBoxes(boxes, class_scores, self.confidence_thresh, self.nms_thresh)

        results = []
        for i in indices:
            class_id = class_ids[i]
            keypoints = self._get_keypoints(objects_keypoints[i])

            keypoints = self._clip_keypoints(keypoints, img.shape[1], img.shape[0])

            results.append(ArmorLabelIO(class_id, keypoints))

        return results

    def _letterbox(self, source: np.ndarray) -> np.ndarray:
        h, w = source.shape[:2]
        _max = max(w, h)
        result = np.full((_max, _max, 3), 114, dtype=np.uint8)
        result[:h, :w] = source
        self.letterbox_scale = _max / max(self.img_size)
        return result

    def _blob_from_image(self, image: np.ndarray) -> np.ndarray:
        resized = cv2.resize(image, self.img_size)
        return cv2.dnn.blobFromImage(
            resized, 
            scalefactor=1/255.0, 
            size=self.img_size,
            swapRB=True,  # BGR to RGB
            crop=False
        )

    def _read_from_output_buffer(self, output_buffer):
        output_buffer = np.squeeze(output_buffer).T
        class_range = [4, 4 + self.num_classes]
        kpts_range = [4 + self.num_classes, 4 + self.num_classes + 2 * self.num_keypoints]

        class_ids = []
        class_scores = []
        boxes = []
        objects_keypoints = []

        for i in range(output_buffer.shape[0]):
            classes_scores = output_buffer[i, class_range[0]:class_range[1]]
            max_score = np.max(classes_scores)

            if max_score > self.confidence_thresh:
                class_id = np.argmax(classes_scores)

                keypoints = []
                kpts = output_buffer[i, kpts_range[0]:kpts_range[1]]
                for j in range(self.num_keypoints):
                    x = kpts[j * 2] * self.letterbox_scale
                    y = kpts[j * 2 + 1] * self.letterbox_scale
                    keypoints.extend([x, y])

                box = self._kpts_to_bbox(keypoints)

                class_ids.append(class_id)
                class_scores.append(float(max_score))
                boxes.append(box)
                objects_keypoints.append(keypoints)

        return class_ids, class_scores, boxes, objects_keypoints

    def _kpts_to_bbox(self, keypoints):
        xs = keypoints[0::2]
        ys = keypoints[1::2]

        x_min = np.min(xs)
        y_min = np.min(ys)
        x_max = np.max(xs)
        y_max = np.max(ys)

        return [x_min, y_min, x_max - x_min, y_max - y_min]

    def _get_keypoints(self, keypoints_flat):
        keypoints = []
        for j in range(self.num_keypoints):
            x = keypoints_flat[2 * j]
            y = keypoints_flat[2 * j + 1]
            keypoints.append((x, y))
        return keypoints

    def _clip_keypoints(self, keypoints, img_w, img_h):
        clipped = []
        for pt in keypoints:
            x = max(0, min(float(pt[0]), img_w - 1))
            y = max(0, min(float(pt[1]), img_h - 1))
            clipped.append((x, y))
        return clipped