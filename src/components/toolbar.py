import pygame
from pygame import Surface, Vector2
from PySide6.QtCore import QRectF
from classes.stats import SimStats
from classes.constants import SIM_WIDTH, SIM_HEIGHT, THEME
class Toolbar():
    WIDTH = 600

    def __init__(self):
        self._surface = Surface((self.WIDTH, 200))
        
        

    def _draw(self, height: int):
        
        self._surface = Surface((self.WIDTH, height))
        
        self._surface.fill(THEME['toolbar_bg'])
        
        
    
    def draw(self, screen: Surface): 
        width, height = screen.get_size()

        self._draw(height)
        
        screen.blit(self._surface, (width-self.WIDTH, 0))        