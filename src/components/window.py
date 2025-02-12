import json
import math
import pygame
from typing import Self, IO
from pygame.time import Clock
from pygame.font import Font
from pygame import Rect, Surface, Vector2
from components.toolbar import Toolbar
from components.simulation import Simulation
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT


class Window():
    WIDTH = 1920
    HEIGHT = 1080
    

    
    def __init__(self, config: IO):
        super().__init__()

        pygame.init()
        
        self._loop_clock = Clock()
        self._paused_clock = Clock()
        self._paused_time = 0

        self._simulation: Simulation = Simulation.from_config(config)
        self._toolbar: Toolbar = Toolbar()
        
        # Screen for drawing with pygame.
        # Initialized in self.run()
        self._screen: Surface = None
        
        
    # Gets current window dimensions
    def _size(self):
        return pygame.display.get_surface().get_size()
    
    def _build_ui(self):
        button_layout_rect = pygame.Rect(30, 20, 100, 20)


        UIButton(relative_rect=Rect(30, 20, 1000, 20),
          text='Hello', manager=self._manager,
            container=self._manager.root_container,
          anchors={'center': 'center'})

    
    def _draw(self):
        simrect = self._simulation.draw(self._screen, 
                                        Vector2(0, 0),
                                        (self._size()[0] - Toolbar.WIDTH,
                                         self._size()[1]))
        self._toolbar.draw(self._screen)
        
        
        

   
    
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
