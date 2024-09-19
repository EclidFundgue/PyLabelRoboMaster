from typing import List, Tuple

import cv2

# Binary threshold value
_THRESH = 180

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

def correctLabelByPoints(img: cv2.Mat, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
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