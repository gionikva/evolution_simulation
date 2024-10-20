from collections.abc import Sequence, Callable
from uuid import uuid4
from pygame import time
from pygame import Vector2, Color
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

class BlobTraits():
    def __init__(self, *, 
                 size: float,
                 speed: float):
        self.size = size
        self.speed = speed

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
    ENERGY_EXP_SIZE_R = 100
    # The ratio of the above two values will equal \
    # the time a blob will survive moving at full speed \
    # given that it started with full energy.
    
    
    # Determines how much energy is spent when \
    # a blob moves at a particular velocity.
    VEL_ENERGY_MULT = 0.0002
    
    ACC_MULTIPLIER = 500.
    
    MIN_SIZE = 2.
    
    
    # Determines how much energy per unit size a blob \
    # loses per second, independent of movement.
    PASSIVE_ENERGY_LOSS = 2.
    
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
                 position=Vector2(0, 0),
                 rng: Generator,
                 hue: float):
        
        self._rng: Generator = rng
        # phenotypic traits:
        self.traits = traits
        # internal variables:
        self.position: Vector2 = position
        
        # unique identifier
        self.id = uuid4().int
        # internal
        self.age = 0.
        # self._candies: set[Candy] = gamestate[1]
        # self._blobs: set[Blob] = gamestate[0]
        self.acc = Vector2(0, 0)
        self.vel = Vector2(0, 0)
        # calculated values
        self.max_energy = self.ENERGY_SIZE_R * self.traits.size
        self.energy = self.max_energy / 2
        # color
        self.color = Color(0, 0, 0)
        self.color.hsla = (hue, 85, 45, 1)
        
    def distance_to(self, other):
        return math.sqrt((self.position.x - other.position.x)**2 +
                         (self.position.y - other.position.y)**2)
    
        
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
    
    # def _move(self, timediff):
    #     candy = self._closest_candy()
    #     dist = self.distance_to(candy)
    #     self._acc = self.ACC_MULTIPLIER * Vector2(candy.position.x - self.position.x,
    #                         candy.position.y - self.position.y) / dist
    #     # self._acc -= self._vel * self.FRICTION 
    #     self._vel += self._acc * timediff
    #     if self._vel.magnitude() > self.traits.speed:
    #         self._vel = self._vel * self.traits.speed / self._vel.magnitude()
    #     # self._vel = min(self._vel, self.traits.speed)
        
    #     movement = (self._vel + 0.5 * self._acc) * timediff
        
    #     self.position += movement
    #     self._energy -= self.ENERGY_EXP_SIZE_R * self.traits.size * movement.magnitude() 
    
    # def _death(self):
    #     pass

    # def _reproduce(self):
    #     pass
        
    # def _lifecycle(self, timediff):
    #     if self._energy <= 0:
    #         self._death()
        
    #     if timediff >= self.LIFESPAN:
    #         if self._energy / self._max_energy >= 0.5:
    #             self._reproduce()
    #         else:
    #             self._death()            
        
    # def on_loop(self):
    #     timediff = self._clock.tick() / 1000
    #     self._move(timediff)
    #     self._lifecycle(timediff)

    def from_traits(size: float,
                    speed: float,
                    position: tuple[float, float]):
        return Blob(traits=BlobTraits(size=size,
                                      speed=speed),
                    position=position)
        
    def random(*, rng: Generator,
                  mean_traits: BlobTraits,
                  sdvs: MutationSdvs,
                  gen_position: Callable[[], Vector2] = None) -> Self:
            size = max(utils.sample_normal(rng=rng,
                                     mean=mean_traits.size,
                                     std_dev=sdvs.size), Blob.MIN_SIZE)
            
            speed = max(utils.sample_normal(rng=rng,
                                      mean=mean_traits.speed,
                                      std_dev=sdvs.speed), 20)
            radius = utils.radius(size) 
            
            if gen_position == None:
                position = Vector2(rng.uniform(radius, SCREEN_WIDTH - radius),
                        rng.uniform(radius, SCREEN_HEIGHT - radius))
            else:
                position = gen_position()
                
            hue = rng.uniform(0., 360.)
            
            position, _ = utils.bound_position(position, radius)
            
            return Blob(traits=BlobTraits(size=size, speed=speed),
                        position=position,
                        hue=hue,
                        rng=rng)
        
    def __hash__(self):
        return self.id

        