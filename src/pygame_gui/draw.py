from typing import List, Sequence, Tuple, Union

from pygame import draw as pg_draw
from pygame.color import Color
from pygame.rect import Rect
from pygame.surface import Surface as pg_Surface

_ColorValue = Union[
    Color, str, Tuple[int, int, int], List[int], int, Tuple[int, int, int, int]
]

def acircle(
    surface: pg_Surface,
    color: _ColorValue,
    center: Union[Tuple[float, float], Sequence[float]],
    radius: float,
    width: int = 0,
) -> None:
    raise NotImplementedError("Not implemented yet")

def rounded_rect(
    surface: pg_Surface,
    color: _ColorValue,
    rect: Union[Rect, Tuple[int, int, int, int]],
    radius: float,
) -> None:
    if isinstance(rect, tuple):
        rect = Rect(rect)

    xl, xr = rect.left + radius, rect.right - radius
    yt, yb = rect.top + radius, rect.bottom - radius
    # draw the rounded corners
    pg_draw.circle(surface, color, (xl, yt), radius)
    pg_draw.circle(surface, color, (xr, yt), radius)
    pg_draw.circle(surface, color, (xl, yb), radius)
    pg_draw.circle(surface, color, (xr, yb), radius)

    # fill the center
    pg_draw.rect(surface, color, (rect.left, yt, rect.width, rect.height - radius * 2))
    pg_draw.rect(surface, color, (xl, rect.top, rect.width - radius * 2, rect.height))