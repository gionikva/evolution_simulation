from pygame import Surface, Rect
from classes.constants import SIM_WIDTH, SIM_HEIGHT
class Statbar():
    HEIGHT = 180
    WIDTH = 80
    def __init__(self,
                 screen: Surface):
        self.screen: Surface = screen
        
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
            self.screen.blit(text1, position)
            self.screen.blit(text2, (position[0], position[1] + margin))
            self.screen.blit(text3, (position[0], position[1] + margin * 2))
        else:
            self.screen.blit(text1, (position[0] - text1.get_width(), position[1]))
            self.screen.blit(text2, (position[0] - text2.get_width(), position[1] + margin))
            self.screen.blit(text3, (position[0] - text3.get_width(), position[1] + margin * 2))
            

    
    def draw(self, lmean: float, rmean: float):
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(0, SIM_HEIGHT-1, SIM_WIDTH, 5))
        pygame.draw.line(self.screen, (0, 0, 0), (SIM_WIDTH/2, SIM_HEIGHT),
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