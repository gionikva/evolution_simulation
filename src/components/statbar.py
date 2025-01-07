from pygame import Surface, Vector2
from PySide6.QtCore import QRectF
from classes.constants import SIM_WIDTH, SIM_HEIGHT
class Statbar():
    WIDTH = 80

    HEIGHT = 180
    def __init__(self):
        self._surface = Surface((self.WIDTH, self.HEIGHT))
        
    def _draw_trait_values(self, *,
                           position: tuple[int, int], 
                           mean_size: float,
                           mean_speed: float,
                           alignleft: bool):
        
        titlefont = pygame.font.SysFont('Noto Sans', 30, True)
        font = pygame.font.SysFont('Noto Sans', 30, False)

        text1 = titlefont.render('Mean Phenotype Values', True, (0, 0, 0))
        text2 = font.render(f'Mean size: {mean_size if mean_size != None else "N/A"}', True, (0, 0, 0))
        text3 = font.render(f'Mean speed: {mean_speed if mean_speed != None else "N/A"}', True, (0, 0, 0))

        text2.get_width()
        
        margin = 50

        if alignleft:
            self._surface.blit(text1, position)
            self._surface.blit(text2, (position[0], position[1] + margin))
            self._surface.blit(text3, (position[0], position[1] + margin * 2))
        else:
            self._surface.blit(text1, (position[0] - text1.get_width(), position[1]))
            self._surface.blit(text2, (position[0] - text2.get_width(), position[1] + margin))
            self._surface.blit(text3, (position[0] - text3.get_width(), position[1] + margin * 2))
            

    
    def _draw(self, lmean: float, rmean: float):
        pygame.draw.rect(self._surface, (0, 0, 0), QRectF(0, SIM_HEIGHT-1, SIM_WIDTH, 5))
        pygame.draw.line(self._surface, (0, 0, 0), (SIM_WIDTH/2, SIM_HEIGHT),
                         (SIM_WIDTH/2, SIM_HEIGHT + self.STATBAR_HEIGHT),
                         5)
                
        self._draw_trait_values(position=(20, SIM_HEIGHT + 20),
                                mean_size=lmean.size,
                                mean_speed=lmean.speed,
                                alignleft=True)
        self._draw_trait_values(position=(SIM_WIDTH / 2 + 20, SIM_HEIGHT + 20),
                                mean_size=rmean.size,
                                mean_speed=rmean.speed,
                                alignleft=True)
    
    def draw(self, screen: Surface, offset: float, bounds: tuple[int, int], means: tuple[float, float]): 
        self._draw(means[0], means[1])
        dims = self.size(bounds)
        pos = ((bounds[0] - dims[0]) / 2, offset)
        
        screen.blit(pygame.transform.smoothscale(self._surface, dims),
                    pos)
        return QRectF(pos[0], pos[1], dims[1], dims[1])
        
        
    def size(self, bounds: tuple[int, int]):
        width, height = bounds
        
        if width / height < SIM_WIDTH / SIM_HEIGHT:
            dims = (width, (SIM_HEIGHT/SIM_WIDTH) * width)
        else:
            dims = (height * (SIM_WIDTH/SIM_HEIGHT), height)
        
        return dims