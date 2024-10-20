import math
from classes.constants import *
from numpy.random import Generator
from pygame import Vector2

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
        
    # Used to bound the position of a blob within the
    # dimensions of the screen.
    def bound_position(position: Vector2, radius: float) -> tuple[Vector2, bool]:
        bx, clampedx = utils._clamp(position.x, radius, SIM_WIDTH-radius)
        by, clampedy =  utils._clamp(position.y, radius, SIM_HEIGHT-radius)
        return (Vector2(bx, by), clampedx or clampedy) 