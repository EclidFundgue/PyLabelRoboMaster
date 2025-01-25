import os
from typing import List, Tuple


def line2ixy(line: str) -> Tuple[int, List[float], List[float]]:
    ls = line.strip().split()
    idx = int(ls[0])
    xs = [float(x) for x in ls[1::2]]
    ys = [float(y) for y in ls[2::2]]
    return idx, xs, ys

def ixy2line(idx: int, xs: List[float], ys: List[float]) -> str:
    ls = [idx]
    for x, y in zip(xs, ys):
        ls.append(x)
        ls.append(y)
    ls = [str(x) for x in ls]
    return ' '.join(ls)

def line2ibxy(line: str) -> Tuple[int, List[float], List[float], List[float]]:
    ls = line.strip().split()
    idx = int(ls[0])
    box = [float(x) for x in ls[1:5]]
    xs = [float(x) for x in ls[5::2]]
    ys = [float(y) for y in ls[6::2]]
    return idx, box, xs, ys

def ibxy2line(idx: int, box: List[float], xs: List[float], ys: List[float]) -> str:
    ls = [idx] + box
    for x, y in zip(xs, ys):
        ls.append(x)
        ls.append(y)
    ls = [str(x) for x in ls]
    return ' '.join(ls)

def xy2box(xs: List[float], ys: List[float]) -> List[float]:
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x = (x_min + x_max) / 2
    y = (y_min + y_max) / 2
    w = x_max - x_min
    h = y_max - y_min
    return [x, y, w, h]

class LabelIO:
    def __init__(self, cls_id: int, kpts: List[Tuple[float, float]]):
        self.cls_id = cls_id
        self.kpts = kpts

class ArmorLabelIO(LabelIO):
    '''
    ArmorLabelIO(_id, kpts)

    id:
    * 0-7:  BG, B1, B2, B3, B4, B5, BO, BB
    * 8-15: RG, R1, R2, R3, R4, R5, RO, RB

    kpts:
    * [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    * lt, lb, rb, rt
    '''

class BuffLabelIO(LabelIO):
    '''
    BuffLabelIO(_id, kpts)

    id:
    * 0: BT, 1: BP, 2: RT, 3: RP

    kpts:
    * [(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5)]
    '''

def loadLabel(path: str) -> List[LabelIO]:
    ''' Load labels from file. '''
    if not os.path.exists(path):
        return []

    with open(path, 'r') as f:
        lines = f.readlines()

    ret: List[LabelIO] = []
    for line in lines:
        idx, box, xs, ys = line2ibxy(line)
        pts = list(zip(xs, ys))
        ret.append(LabelIO(idx, pts))

    return ret

def saveLabel(path: str, labels: List[LabelIO]) -> None:
    ''' Save labels to file. '''
    if os.path.exists(path) and len(labels) == 0:
        os.remove(path)

    if len(labels) == 0:
        return

    lines = []
    for lb in labels:
        idx = lb.cls_id
        xs = [p[0] for p in lb.kpts]
        ys = [p[1] for p in lb.kpts]
        bbox = xy2box(xs, ys)
        lines.append(ibxy2line(idx, bbox, xs, ys))

    with open(path, 'w') as f:
        f.write('\n'.join(lines))