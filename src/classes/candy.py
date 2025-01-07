import math
from collections.abc import Callable
from uuid import uuid4
from pygame import Rect
from PySide6.QtGui import QVector2D, QBrush, QPen, QColor
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtCore import Qt
from classes.constants import *
from classes.utils import *
from numpy.random import Generator
from typing import Self




class Candy():
    COLOR = 0xE14BF4
    
    # Determines how much energy a piece \
    # of candy will provide per unit size.
    # ENERGY_SIZE_RATIO = 2000    
    # The time it takes for a piece of candy \
    # to perish after it appears.
    SHELF_LIFE = 15
    
    MIN_SIZE = 2.
    
    def __init__(self, *,
                 size = 2.0,
                 position=QVector2D(0.0, 0.0),
                 rng: Generator):
        self.size = size
        self.time_to_perish: float = self.SHELF_LIFE
        self.position: QVector2D = position
        
        self.id = uuid4().int
        self._rng: Generator = rng
        
        self._create_graphics_item()

    def radius(self) -> float:
        return utils.radius(self.size)
    
    def random(*, rng: Generator,
                  mean_size: float,
                  sdv: float,
                  bounds: Rect,
                  gen_position: Callable[[], QVector2D] = None) -> Self:
        size = max(utils.sample_normal(rng=rng,
                                 mean=mean_size,
                                 std_dev=sdv),
                   Candy.MIN_SIZE)
        
        radius = utils.radius(size)
        
        if bounds.bottom - bounds.top < radius * 2:
            return None
        
        position = QVector2D(rng.uniform(bounds.left, bounds.right),
                    rng.uniform(bounds.top + radius, bounds.bottom - radius))
        
        return Candy(size=size,
                     position=position,
                     rng=rng)
        
    # creates and saves the QGraphicsItem (ellipse)
    # for rendering purposes
    def _create_graphics_item(self):
        d = self.radius()*2
        
        self._ellipse = QGraphicsEllipseItem(self.position.x()-d/2,
                                             self.position.y()-d/2, 
                                             d,
                                             d)

        self._ellipse.setPen(QPen(Qt.NoPen))
        self._ellipse.setBrush(QBrush(QColor(self.COLOR)))
    
    def __hash__(self):
        return self.id
        