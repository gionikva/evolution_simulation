import math
from classes.constants import *
from numpy.random import Generator
from PySide6.QtGui import QVector2D
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem
from PySide6.QtCore import QRectF

class utils:
    def radius(size: float) -> float:
        return math.sqrt(size * SIZE_SCALE / (2 * math.pi))

    def sample_normal(*, rng: Generator,
                    mean: float,
                    std_dev: float,
                    ) -> float:
            return rng.normal() * std_dev + mean
        
    def sample_lognormal(*, rng: Generator,
                    mean: float,
                    std_dev: float,
                    ) -> float:
            return rng.lognormal() * std_dev + mean
        
    # Ensures that a value is between start and end. 
    # The 1-st index of the return value indicates
    # whether the value was changed or "clamped."
    def _clamp(value: float, start: float, end: float) -> tuple[float, bool]:
        clamped = min(max(start, value), end)
        return (clamped, clamped == value)
    
    def rect_intersect(position: QVector2D, radius: float, rect: QRectF) -> tuple[bool, QVector2D]:
        cleft, cright = (position.x() - radius, position.x() + radius)
        ctop, cbottom = (position.y() - radius, position.y() + radius)
                    
        if rect.top() <= position.y() <= rect.bottom():
            if cright > rect.left() and cleft < rect.left():
                return (True, QVector2D(rect.left() - radius, position.y()))
            
            if cleft < rect.right() and cright > rect.right():
                return (True, QVector2D(rect.right() + radius, position.y()))
    
        if rect.left() <= position.x() <= rect.right():
            if ctop < rect.bottom() and cbottom > rect.bottom():
                return (True, QVector2D(position.x(), rect.bottom() + radius))
            
            if cbottom > rect.top() and ctop < rect.top():
                return (True, QVector2D(position.x(), rect.top() - radius))
            
        for corner in [rect.bottomLeft(), rect.bottomRight(), rect.topLeft(), rect.topRight()]:
            
            dist = math.sqrt((corner.x() - position.x())**2 + (corner.y()-position.y())**2)
            if dist < radius:
                s = QVector2D(corner.x() - position.x(), corner.y() - position.y())
                r = (s / s.length()) * radius
                m = s - r
                return (True, position + m)
                    
        return (False, None)
    
    # Used to bound the position of a blob within the
    # dimensions of the screen.
    def bound_position(position: QVector2D, radius: float, separators: tuple[QRectF, QRectF]) -> tuple[QVector2D, bool]:
        bx, clampedx = utils._clamp(position.x(), radius, SIM_WIDTH-radius)
        by, clampedy =  utils._clamp(position.y(), radius, SIM_HEIGHT-radius)
        pos = QVector2D(bx, by)
    
        top, bottom = separators
        
        for rect in [top, bottom]:
            _, newpos = utils.rect_intersect(pos, radius, rect)
            if newpos != None:
                pos = newpos
                
        return pos