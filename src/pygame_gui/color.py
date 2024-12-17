from typing import Tuple


class LightColorTheme:
    Primary = (103, 80, 164)
    OnPrimary = (255, 255, 255)
    PrimaryContainer = (234, 221, 255)
    OnPrimaryContainer = (79, 55, 139)

    Secondary = (98, 91, 113)
    OnSecondary = (255, 255, 255)
    SecondaryContainer = (232, 222, 248)
    OnSecondaryContainer = (74, 68, 88)

    Tertiary = (125, 82, 96)
    OnTertiary = (255, 255, 255)
    TertiaryContainer = (255, 216, 228)
    OnTertiaryContainer = (99, 59, 72)

    Error = (179, 38, 30)
    OnError = (255, 255, 255)
    ErrorContainer = (249, 222, 220)
    OnErrorContainer = (140, 29, 24)

    Surface = (254, 247, 255)
    OnSurface = (29, 27, 32)
    SurfaceVariant = (231, 224, 236)
    OnSurfaceVariant = (73, 69, 79)
    SurfaceContainerHighest = (230, 224, 233)
    SurfaceContainerHigh = (236, 230, 240)
    SurfaceContainer = (243, 237, 247)
    SurfaceContainerLow = (247, 242, 250)
    SurfaceContainerLowest = (255, 255, 255)
    InverseSurface = (50, 47, 53)
    InverseOnSurface = (245, 239, 247)
    SurfaceTint = (103, 80, 164)
    SurfaceTintColor = (103, 80, 164)

    Outline = (121, 116, 126)
    OutlineVariant = (202, 196, 208)

def _setEelevation(color: Tuple[int, int, int], elevation: int) -> Tuple[int, int, int]:
    '''
    Elevation is an integer between 0 and 12.
    For static widget, elevation should not larger than 6.
    7 to 12 for interacting, such as dragging, hovering, etc.

    Five levels of recommended elevations are [1, 3, 6, 8, 12]
    '''
    r, g, b = color
    r = int(r - 8 * elevation)
    g = int(g - 8 * elevation)
    b = int(b - 8 * elevation)
    return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

def dark(color: Tuple[int, int, int], elevation: int) -> Tuple[int, int, int]:
    return _setEelevation(color, elevation)

def light(color: Tuple[int, int, int], elevation: int) -> Tuple[int, int, int]:
    return _setEelevation(color, -elevation)