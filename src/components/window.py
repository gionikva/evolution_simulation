import json
import pygame
from typing import Self, IO
from pygame.time import Clock
from pygame.font import Font
from pygame import Rect
from classes.blob import *
from classes.candy import Candy
from components.statbar import Statbar
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT
import math
from numpy import random

class Window():
    
    
    def __init__(self):
        pygame.init()
        
        self._simulation: Simulation = Simulation()
        self._statbar: Statbar = Statbar()
        
    def _draw():
        self._draw_simulation()
        self._draw_statbar()
        
    def run(self):
       

        self.screen = pygame.display.set_mode([self.SIM_WIDTH,
                                            self.SIM_HEIGHT+self.STATBAR_HEIGHT],
                                                pygame.RESIZABLE)

        self._loop_clock.tick()
        self._paused_clock.tick()
                
        running = True
        paused = False

        while running:
            if not paused:
                self.on_loop()
            else:
                self._paused_time += self._paused_clock.tick() / 1000

            pressed_keys = pygame.key.get_pressed()
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            self._paused_clock.tick()
                        else:
                            self._loop_clock.tick()

            
            self.screen.fill((255, 255, 255))
            
            self._draw()

            pygame.display.flip()
        
        pygame.quit()
