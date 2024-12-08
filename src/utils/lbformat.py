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