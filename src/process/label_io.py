import os
from typing import List, Tuple

from ..utils import lbformat as fmt


class LabelInputOutput:
    def __init__(self, _id: int, kpts: List[Tuple[float, float]]):
        # 0-7:  BG, B1, B2, B3, B4, B5, BO, BB
        # 8-15: RG, R1, R2, R3, R4, R5, RO, RB
        self.id = _id

        # e.g [(0.1, 0.2), (0.1, 0.3), (0.3, 0.3), (0.3, 0.2)]
        # lt, lb, rb, rt
        self.kpts = kpts

def loadLabel(path: str) -> List[LabelInputOutput]:
    ''' Load labels from file. '''
    if not os.path.exists(path):
        return []

    with open(path, 'r') as f:
        lines = f.readlines()

    ret: List[LabelInputOutput] = []
    for line in lines:
        idx, box, xs, ys = fmt.line2ibxy(line)
        pts = list(zip(xs, ys))
        ret.append(LabelInputOutput(idx, pts))

    return ret

def saveLabel(path: str, labels: List[LabelInputOutput]) -> None:
    ''' Save labels to file. '''
    if os.path.exists(path) and len(labels) == 0:
        os.remove(path)

    if len(labels) == 0:
        return

    lines = []
    for lb in labels:
        idx = lb.id
        xs = [p[0] for p in lb.kpts]
        ys = [p[1] for p in lb.kpts]
        bbox = fmt.xy2box(xs, ys)
        lines.append(fmt.ibxy2line(idx, bbox, xs, ys))

    with open(path, 'w') as f:
        f.write('\n'.join(lines))