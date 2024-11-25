from typing import List, Optional, Sequence, Tuple, Union

from pygame import draw as pg_draw
from pygame import transform as pg_transform
from pygame.color import Color
from pygame.locals import SRCALPHA
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
    blend: float = 2,
    draw_top_right: Optional[bool] = False,
    draw_top_left: Optional[bool] = False,
    draw_bottom_left: Optional[bool] = False,
    draw_bottom_right: Optional[bool] = False,
) -> None:
    _radius = radius * (blend + 1)
    _surface = pg_Surface((_radius * 2, _radius * 2), SRCALPHA)
    pg_draw.circle(
        _surface,
        color,
        (_radius, _radius),
        _radius,
        width,
        draw_top_right,
        draw_top_left,
        draw_bottom_left,
        draw_bottom_right,
    )
    _surface = pg_transform.smoothscale(_surface, (radius * 2, radius * 2))
    surface.blit(_surface, (center[0] - radius, center[1] - radius))

def rounded_rect(
    surface: pg_Surface,
    color: _ColorValue,
    rect: Union[Rect, Tuple[int, int, int, int]],
    radius: float,
) -> None:
    if isinstance(rect, tuple):
        rect = Rect(rect)
    _surface = pg_Surface(rect.size, SRCALPHA)

    # draw the rounded corners
    acircle(_surface, color, (radius, radius), radius, draw_top_left=True)
    acircle(_surface, color, (rect.width - radius, radius), radius, draw_top_right=True)
    acircle(_surface, color, (radius, rect.height - radius), radius, draw_bottom_left=True)
    acircle(_surface, color, (rect.width - radius, rect.height - radius), radius, draw_bottom_right=True)

    # fill the center
    pg_draw.rect(_surface, color, (radius, 0, rect.width - radius * 2, rect.height))
    pg_draw.rect(_surface, color, (0, radius, rect.width, rect.height - radius * 2))

    surface.blit(_surface, rect.topleft)