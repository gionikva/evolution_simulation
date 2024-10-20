from collections.abc import Callable
from uuid import uuid4
from pygame import Vector2
import math
from classes.constants import *
from classes.utils import *
from numpy.random import Generator
from typing import Self




class Candy():
    # Determines how much energy a piece \
    # of candy will provide per unit size.
    # ENERGY_SIZE_RATIO = 2000    
    # The time it takes for a piece of candy \
    # to perish after it appears.
    SHELF_LIFE = 15
    
    MIN_SIZE = 2.
    
    def __init__(self, *,
                 size = 2.0,
                 position=Vector2(0.0, 0.0),
                 rng: Generator):
        self.size = size
        self.time_to_perish: float = self.SHELF_LIFE
        self.position: Vector2 = position
        
        self.id = uuid4().int
        self._rng: Generator = rng

    def radius(self) -> float:
        return utils.radius(self.size)
    
    def random(*, rng: Generator,
                  mean_size: float,
                  sdv: float,
                  gen_position: Callable[[], Vector2] = None) -> Self:
        size = max(utils.sample_normal(rng=rng,
                                 mean=mean_size,
                                 std_dev=sdv),
                   Candy.MIN_SIZE)
        
        radius = utils.radius(size)
        
        position = Vector2(rng.uniform(radius, SCREEN_WIDTH - radius),
                    rng.uniform(radius, SCREEN_HEIGHT - radius))
        
        return Candy(size=size,
                     position=position,
                     rng=rng)
    
    def __hash__(self):
        return self.id
        