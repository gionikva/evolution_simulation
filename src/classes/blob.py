from collections.abc import Sequence, Callable
from uuid import uuid4
from pygame import time, Color, Rect
from PySide6.QtGui import QVector2D, QBrush, QPen, QColor
from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtCore import Qt
from classes.candy import Candy
from classes.constants import *
from classes.utils import *
from numpy.random import Generator
from typing import Self
import math



class MutationSdvs():
    def __init__(self,*,
                 size_sdv: float = 5.0,
                 speed_sdv: float = 2.0):
        self.size = size_sdv
        self.speed = speed_sdv
        
    def from_dict(obj: dict) -> Self:
        return MutationSdvs(size_sdv=obj.get('size_sdv'),
                        speed_sdv=obj.get('speed_sdv'))

class BlobTraits():
    def __init__(self, *, 
                 size: float,
                 speed: float):
        self.size = size
        self.speed = speed
    
    def from_dict(obj: dict) -> Self:
        return BlobTraits(size=obj.get('size'),
                          speed=obj.get('speed'))

# Represents a single individual
# Will be rendered as a moving circle
class Blob():
    
    # The lifespan of a single blob.
    # If a blob manages to survive this long, \
    # it splits into floor(energy/size) offspring.
    LIFESPAN = 5.0
    
    # Defines the energy/size ratio.
    ENERGY_SIZE_R = 10000.0
    
    # Defines the energy_expenditure/size ratio.
    ENERGY_EXP_SIZE_R = 3
    # The ratio of the above two values will equal \
    # the time a blob will survive moving at full speed \
    # given that it started with full energy.
    
    
    # Determines how much energy is spent when \
    # a blob moves at a particular velocity.
    VEL_ENERGY_MULT = 0.001
    
    ACC_MULTIPLIER = 500.
    
    MIN_SIZE = 2.
    
    
    # Determines how much energy per unit size a blob \
    # loses per second, independent of movement.
    PASSIVE_ENERGY_LOSS = 10.
    
    # Traits:
    #
    # size:
    # Radius of the blob.
    # Must be at least 50% larger than a piece \
    # of candy or prey to consume it.  
    # 
    # speed:
    # Represents the top speed of the blob.
    # This can affect energy expenditure.
    #
    # Dependent values:
    #
    # energy:
    # Represents the total energy this blob can store.
    # If the blob runs out of energy, it dies.
    # This also determines how many offspring the blob \
    # can produce. Depends on size. Size also determines \
    # energy expenditure.
    #
    # 
    def __init__(self, *,
                 traits = BlobTraits(size = 20.0,
                                    speed = 5.0),
                 position=QVector2D(0, 0),
                 rng: Generator,
                 hue: float):
        
        self._rng: Generator = rng
        # phenotypic traits:
        self.traits = traits
        # internal variables:
        self.position: QVector2D = position
        
        # unique identifier
        self.id = uuid4().int
        # internal
        self.age = 0.
        # self._candies: set[Candy] = gamestate[1]
        # self._blobs: set[Blob] = gamestate[0]
        self.acc = QVector2D(0, 0)
        self.vel = QVector2D(0, 0)
        # calculated values
        self.max_energy = self.ENERGY_SIZE_R * self.traits.size
        self.energy = self.max_energy / 2
        # color
        self.color = Color(0, 0, 0)
        self.color.hsla = (hue, 85, 45, 1)
        
        self._create_graphics_item(hue)
        
    # creates QGraphicsItem needed to render the blob
    
        
    def distance_to(self, other):
        return math.sqrt((self.position.x() - other.position.x())**2 +
                         (self.position.y() - other.position.y())**2)
    
        
    def time_born(self, paused_time: float, speed: float = 1.):
        return (self._time_born - paused_time) * speed
        
    def closest_candy(self, candies, visible: Callable[[Candy], bool]) -> Candy:
        min_pair = (None, 0)
        for candy in candies:
            dist = self.distance_to(candy)
            if (min_pair[0] == None or \
               dist < min_pair[1]) and \
               visible(candy):
                min_pair = (candy, dist)
        return min_pair[0]
    
    def radius(self) -> float:
        return utils.radius(self.traits.size)
    
    def age_by(self, time: float):
        self.age += time
        
    # creates and saves the QGraphicsItem (ellipse)
    # for rendering purposes
    def _create_graphics_item(self, hue: float):
        d = utils.radius(self.traits.size)*2
        
        self._ellipse = QGraphicsEllipseItem(self.position.x()-d/2,
                                             self.position.y()-d/2, 
                                             d,
                                             d)
        

        self._ellipse.setPen(QPen(Qt.NoPen))
        self._ellipse.setBrush(QBrush(QColor.fromHslF(hue, 1, 0.5, 1.)))
    
    def _move(self, 
              candies: list[Candy],
              blobs: list[Self],
              separators: tuple[Rect, Rect],
              timediff: float):
        def visible(candy: Candy) -> bool:
            for sep in separators:
                if sep.clipline((self.position.x(), self.position.y()),
                                (candy.position.x(), candy.position.y())) != ():
                    return False
            return True
        
        candy = self.closest_candy(candies, visible)
        
        if candy == None:
            return
        
        dist = self.distance_to(candy)
        displacement = QVector2D(candy.position.x() - self.position.x(),
                            candy.position.y() - self.position.y())
        
        
        # New (basic) movement logic
        # d_norm = displacement / displacement.magnitude()
        
        # blob.vel = d_norm * blob.traits.speed
        
        # movement = blob.vel * timediff
        
        # Old movement logic
        
        self.acc = Blob.ACC_MULTIPLIER * displacement / dist
        # self._acc -= self._vel * self.FRICTION 
        self.vel += self.acc * timediff
        
        
       
        
        if self.vel.magnitude() > self.traits.speed:
            self.vel = self.vel * self.traits.speed / self.vel.magnitude()
        # self._vel = min(self._vel, self.traits.speed)
        
        fvel = self.vel + 0.2 * self.acc
        
        if fvel.magnitude() > self.traits.speed:
            fvel = fvel * self.traits.speed / fvel.magnitude()
        
        movement = fvel * timediff
                

        oldpos = self.position
        
        self.position = utils.bound_position(self.position + movement, self.radius(), separators)

        movement = self.position - oldpos
        
        # slope = movement.y() / movement.x()
            
        self.energy -= (Blob.ENERGY_EXP_SIZE_R * self.traits.size) * movement.magnitude() * \
            (1 + Blob.VEL_ENERGY_MULT * self.vel.magnitude())
    
    def _death(self):
        pass

    def _reproduce(self):
        pass
        
    def _lifecycle(self, timediff):
        if self._energy <= 0:
            self._death()
        
        if timediff >= self.LIFESPAN:
            if self._energy / self._max_energy >= 0.5:
                self._reproduce()
            else:
                self._death()            
        
    def on_loop(self):
        timediff = self._clock.tick() / 1000
        self._move(timediff)
        self._lifecycle(timediff)

    def from_traits(size: float,
                    speed: float,
                    position: tuple[float, float]):
        return Blob(traits=BlobTraits(size=size,
                                      speed=speed),
                    position=position)
        
    def random(*, rng: Generator,
                  mean_traits: BlobTraits,
                  sdvs: MutationSdvs,
                  separators: tuple[Rect, Rect],
                  gen_position: Callable[[], QVector2D] = None) -> Self:
            size = max(utils.sample_normal(rng=rng,
                                     mean=mean_traits.size,
                                     std_dev=sdvs.size), Blob.MIN_SIZE)
            
            speed = max(utils.sample_normal(rng=rng,
                                      mean=mean_traits.speed,
                                      std_dev=sdvs.speed), 20)
            radius = utils.radius(size) 
            
            if gen_position == None:
                position = QVector2D(rng.uniform(radius, SIM_WIDTH - radius),
                        rng.uniform(radius, SIM_HEIGHT - radius))
            else:
                position = gen_position()
                
            hue = rng.uniform(0., 1.)
            
            position = utils.bound_position(position, radius, separators)
            
            return Blob(traits=BlobTraits(size=size, speed=speed),
                        position=position,
                        hue=hue,
                        rng=rng)
        
    def __hash__(self):
        return self.id

        