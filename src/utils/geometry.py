from math import acos
from math import pi as PI
from math import sqrt
from typing import List, Tuple


def __zero(value) -> bool:
    return abs(value) < 1e-6

def __positive(value) -> bool:
    return value > 1e-6

def __len(vec) -> float:
    return sqrt(vec[0] * vec[0] + vec[1] * vec[1])

def __sub(p1, p2) -> Tuple[float, float]:
    return (p1[0] - p2[0], p1[1] - p2[1])

def __dot(p1, p2) -> float:
    return p1[0] * p2[0] + p1[1] * p2[1]

def __constrain(value, _min, _max) -> float:
    return max(min(value, _max), _min)


def __get_radian(pA, pO, pB) -> float:
    ''' radian of angle AOB, > 0 if clockwize '''
    OA = __sub(pA, pO)
    OB = __sub(pB, pO)

    # O is A or B
    if __zero(__len(OA)) or __zero(__len(OB)):
        return None

    dotAOB = __dot(OA, OB)
    abs_res = acos(__constrain(dotAOB / __len(OA) / __len(OB), -1, 1))
    nA = (OA[1], -OA[0]) # OA counterclockwise 90 degrees
    sign = __dot(nA, OB)

    if __zero(sign): # OA OB in a line
        # dotAOB < 0: O in AB
        return 0 if __positive(dotAOB) else None

    if __positive(sign):
        return abs_res
    return -abs_res

# point in polygon
def in_polygon(
        polygon: List[Tuple[float, float]],
        point: Tuple[float, float]
        ) -> bool:
    '''
    Test if point in polygon.
    Return `None` if point in a line of this polygon.
    '''
    res = 0.0
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        radius = __get_radian(p1, point, p2)
        # point in a line of this polygon
        if radius is None:
            return None
        res += radius

    # outside: res = 0, inside: res = 2PI or -2PI
    return abs(res) > PI