import pygame
from pygame import Surface as pg_Surface

from ..pygame_gui import BaseComponent


class LoadingFrame(BaseComponent):
    def __init__(self, w: int, h: int, text: str):
        super().__init__(w, h, 0, 0)

        self.text = text
        self.font = pygame.font.SysFont('simsun', 30)
        self.text_img = self.font.render(self.text, True, (255, 255, 255))

    def draw(self, surface: pg_Surface) -> None:
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.w, self.h))
        text_w, text_h = self.text_img.get_size()
        surface.blit(
            self.text_img,
            (self.x + self.w - text_w,
             self.y + self.h - text_h)
        )
        