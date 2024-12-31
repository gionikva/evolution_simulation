import json
import pygame
from typing import Self, IO
from pygame.time import Clock
from pygame.font import Font
from pygame import Rect, Surface
from classes.blob import *
from classes.candy import Candy
from components.statbar import Statbar
from components.simulation import Simulation
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT
import math
from numpy import random

class Window():
    WIDTH = 1920
    HEIGHT = 1080
    
    def __init__(self, config: IO):
        pygame.init()
        
        self._loop_clock = Clock()
        self._paused_clock = Clock()
        self._paused_time = 0

        self._simulation: Simulation = Simulation.from_config(config)
        # self._statbar: Statbar = Statbar()
        
        # Screen for drawing with pygame.
        # Initialized in self.run()
        self._screen: Surface = None
        
    def _draw(self):
        self._simulation.draw(self._screen, Vector2(0, 0))
        
    def run(self):
        self._screen = pygame.display.set_mode([self.WIDTH,
                                                self.HEIGHT],
                                                pygame.RESIZABLE)

        running = True

        while running:
            self._simulation.on_loop()

            pressed_keys = pygame.key.get_pressed()
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self._simulation.playpause()

            
            self._screen.fill((255, 255, 255))
            
            self._draw()

            pygame.display.flip()
        
        pygame.quit()
