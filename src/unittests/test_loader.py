import pygame

from .. import resources_loader

pygame.init()
screen = pygame.display.set_mode()

def test_Loader():
    loader = resources_loader.ImageLoader()
    print(loader.image_dict)