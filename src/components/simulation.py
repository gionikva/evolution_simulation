import math
import json
import pygame
from pygame import Surface
from typing import Self, IO
from classes.blob import *
from classes.candy import Candy
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT
from numpy import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QLabel, QHBoxLayout, QGraphicsRectItem, QFrame
from PySide6.QtCore import QRectF, Qt, QThread, QTimer, QElapsedTimer
from PySide6.QtGui import QTransform, QBrush, QPen


class Simulation(QWidget):
    SIM_WIDTH=SIM_WIDTH
    SIM_HEIGHT=SIM_HEIGHT
    
    SEPARATOR_WIDTH = 80
    
    N_INTERVALS = 100

    BLOB_COLOR = (100, 100, 255)
    CANDY_COLOR = (146, 77, 155)
    FRICTION = 0.1
    
    # Whether the candy should be regenerated for each generation.
    RESET_CANDY_PER_LIFESPAN = True
    
    # Limit after which candy will start to disappear.
    # This is here to maintain performance.
    CANDY_LIMIT = 500
        
    def __init__(self, *,
                # Rng seed
                seed: int = None,
                        
                # Mean trait values for the starting population
                mean_traits: BlobTraits = BlobTraits(size = 20.0,
                                         speed = 300.0),
                
                # Mean candy size
                mean_candy_sizes: tuple[float, float] = (5.0, 5.0),
                
                # Mutation standard deviation
                mutation_sdvs: MutationSdvs = MutationSdvs(size_sdv = 5,
                                             speed_sdv = 2),
                initial_sdvs: MutationSdvs = MutationSdvs(size_sdv = 5,
                                             speed_sdv = 2),
                
                # Candy size standard deviation
                candy_size_sdvs: tuple[float, float] = (2.0, 2.0),
                
                # Starting number of candy
                n_candies: tuple[int, int] = (20, 20),
                candy_spawn_rates: tuple[float, float] = (10, 10),
                
                # Energy a candy provides when \
                # eaten per unit size.
                candy_energy_density: float = 2000,
                
                cutoff_sharpness: float = 2,
                        
                # Starting number of blobs
                n_blobs: int = 10,
                
                
                separation_gap: float = 1,
                sim_speed: float = 1
                ):

        super().__init__()
        self._seed = seed
        self._mean_traits = BlobTraits(size=mean_traits.size,
                                      speed=mean_traits.speed)
     
        self._initial_sdvs = initial_sdvs
        
        self._surface = Surface((SIM_WIDTH, SIM_HEIGHT))
        
        '''Simulation parameters'''
        self._mutation_sdvs = MutationSdvs(size_sdv=mutation_sdvs.size,
                                           speed_sdv=mutation_sdvs.speed)
        self._candy_energy_d = candy_energy_density
        self._rng = random.default_rng(seed=seed)
        self._gap = separation_gap
        self._sim_speed = sim_speed
        self._mean_candy_sizes = mean_candy_sizes
        self._candy_size_sdvs = candy_size_sdvs
        self._candy_spawn_rates = candy_spawn_rates
        self._n_candies = n_candies
        self._n_blobs = n_blobs
        self._cutoff_sharpness = cutoff_sharpness
        
        # Indicates whether simulation is paused (can be updated externally)
       
        self._setupUi()

    def _setupUi(self):
        self.scene = QGraphicsScene(0, 0, self.SIM_WIDTH, self.SIM_HEIGHT)

        self.scene.addRect(0., 0.,self.SIM_WIDTH, self.SIM_HEIGHT,
                           QPen(Qt.NoPen),
                           QBrush(Qt.white))
        
        self._paused = False
        
        self._intervals: list[QRectF] = self._gen_intervals()
        
        self._candies = self._gen_initial_candies(self._n_candies)
        self._blobs = self._gen_initial_blobs(self._n_blobs)
        
        self._loop_clock = QElapsedTimer() 
        self._loop_clock.start()
                
        self._time: float = 0    

        self._graphics = QGraphicsView(self.scene, self)
                
        self._graphics.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


        self._layout = QHBoxLayout(self)
        self._layout.addWidget(self._graphics)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_loop)
        self.timer.start(0)

        self.add_items()
    
    def updateView(self):
        r = self.scene.sceneRect()
        self._graphics.fitInView(r, Qt.KeepAspectRatio)
    
    def resizeEvent(self, event):
        self.updateView()
    def showEvent(self, event):
        self.updateView()
        
    def from_config(file: IO) -> Self:
        config: dict = json.load(file)
        print(config)
        return Simulation(
            seed=config.get('seed'),
            mean_traits=BlobTraits.from_dict(config.get('mean_traits') or {'size': 20., 'speed': 300.}),
            mean_candy_sizes=tuple(config.get('mean_candy_sizes') or [5., 5.]),
            mutation_sdvs=MutationSdvs.from_dict(config.get('mutation_sdvs') or {'size_sdv': 5., 'speed_sdv': 2.}),
            initial_sdvs=MutationSdvs.from_dict(config.get('initial_sdvs') or {'size_sdv': 5., 'speed_sdv': 2.}),
            candy_size_sdvs=tuple(config.get('candy_size_sdvs') or [2., 2.]),
            n_candies=tuple(config.get('n_candies') or [20, 20]),
            candy_spawn_rates=tuple(config.get('candy_spawn_rates') or [20, 20]),
            candy_energy_density=config.get('candy_energy_density') if 'candy_energy_density' in config else 2000.,
            cutoff_sharpness=config.get('cutoff_sharpness') if 'cutoff_sharpness' in config else 3.,
            n_blobs=config.get('n_blobs') if 'n_blobs' in config else 10,
            separation_gap=config.get('separation_gap') if 'separation_gap' in config else 1.,
            sim_speed=config.get('sim_speed') if 'sim_speed' in config else 1.
        )
    
     
    def mean_traits(self) -> tuple[BlobTraits, BlobTraits]:
        leftsums = BlobTraits(size=0., speed=0.)
        rightsums = BlobTraits(size=0., speed=0.)
        
        nleft = 0
        nright = 0
        
        for blob in self._blobs:
            if blob.position.x() < SIM_WIDTH / 2:
                leftsums.size += blob.traits.size
                leftsums.speed += blob.traits.speed
                nleft += 1
            else:
                rightsums.size += blob.traits.size
                rightsums.speed += blob.traits.speed
                nright += 1
        
        if nleft != 0:
            lmean = BlobTraits(size = leftsums.size / nleft,
                                speed = leftsums.speed / nleft)
        else:
            lmean = BlobTraits(size = None,
                                speed = None)
        
        if nright != 0:
            rmean = BlobTraits(size = rightsums.size / nright,
                                speed = rightsums.speed / nright)
        else:
            rmean = BlobTraits(size = None,
                                speed = None)
        return (lmean,
                rmean)
      
    # Toggles the paused state of the simulation
    def playpause(self) -> bool:
        self._paused = not self._paused
        
        if not self._paused:
            self._loop_clock.tick()
        
        return self._paused
    
    
    def on_loop(self):
        if self._paused: return
        
        timediff = self._sim_speed * self._loop_clock.nsecsElapsed() / 1000000000
        self._loop_clock.restart()
        
        self._time += timediff
        
        deadblobs = []
        newblobs = []
        
        for blob in self._blobs:
            eaten_candies = self._move_blob(blob, timediff)
        #     self._passive_energy_loss(blob, timediff)
        #     blob.age_by(timediff)
        #     dead, offspring = self._lifecycle_blob(blob, timediff)
            
        #     if dead:
        #         deadblobs.append(blob)
            
        #     newblobs.extend(offspring)
            
        #     eaten_candies = self._eat(blob)
            
        #     for eaten in eaten_candies:
        #         self._candies.remove(eaten)           
        
        # for blob in deadblobs:
        #     if blob in self._blobs:
        #         self._blobs.remove(blob)
        
        # for blob in newblobs:
        #     self._blobs.add(blob)
            
        # self._spawn_candy(timediff)
    
        
    def add_items(self) -> QRectF:
        # self._surface.fill((255, 255, 255))
        self._add_candies()
        self._add_blobs()
        # self._draw_separators()
        
       
        # dims = self.size(bounds)
        # pos = ((bounds[0] - dims[0]) / 2, (bounds[1] - dims[1]) / 2)
        
        # screen.blit(pygame.transform.smoothscale(self._surface, dims),
        #             pos)
        # return Rect(pos[0], pos[1], dims[1], dims[1])
        
        
    def size(self, bounds: tuple[int, int]):
        width, height = bounds
        
        if width / height < SIM_WIDTH / SIM_HEIGHT:
            dims = (width, (SIM_HEIGHT/SIM_WIDTH) * width)
        else:
            dims = (height * (SIM_WIDTH/SIM_HEIGHT), height)
        
        return dims
  
    
    def _interpolate(self, *, x: float, range: tuple[float, float]):
        low, high = range
        x = x / self.SIM_WIDTH
        
        # Steepness.
        # k=1 is a line
        k = self._cutoff_sharpness
        
        rawval = 1 - (1 / (1 + (1 / x - 1)**(-k)))
        
        scaled = (high - low) * rawval + low
        
        return scaled
        
        # slope = (range[1] - range[0]) / self.SCREEN_WIDTH
        # return slope * x + range[0]
    
    def _interval_width(self):
        return self.SIM_WIDTH / self.N_INTERVALS
    
    def _gen_interval(self, i: int) -> QRectF:
        left = self._interval_width() * i
        width = self._interval_width()
        rect = QRectF(left,
                     0, 
                     width,
                     self.SIM_HEIGHT)
        
        separators = self._separators()
        
    
        
        rect.intersects(separators[0])
    
        # checks if either separator intersects with the interval
        if any(map(lambda s: rect.intersects(s), separators)):
            rect = QRectF(left,
                         separators[0].bottom(),
                         width,
                         self._gap * self.SIM_HEIGHT)
        
        return rect
    
    def _gen_intervals(self) -> list[QRectF]:
        return [self._gen_interval(i) for i in range(self.N_INTERVALS)]
            
    
    def _radius(self, size: float) -> float:
        return math.sqrt(size * SIZE_SCALE / (2 * math.pi))
        
    def _gen_initial_blobs(self, n):
        blobs = set()
        for i in range(n):
            blob = Blob.random(mean_traits=self._mean_traits,
                                  sdvs=self._initial_sdvs,
                                  separators=self._separators(),
                                  rng=self._rng)
            blob.position = utils.bound_position(blob.position, blob.radius(), self._separators())
            blobs.add(blob)
        return blobs
    
   
    def _generate_candies(self, n: int,
                          mean_size: float,
                          sdv: float,
                          region: QRectF) -> list[Candy]:
        candies = []
        for i in range(n):
            candy = Candy.random(mean_size=mean_size,
                                     sdv=sdv,
                                     rng=self._rng,
                                     bounds=region)
            candy.position = utils.bound_position(candy.position, candy.radius(), self._separators())
            candies.append(candy)
        return candies
    
    def _gen_initial_candies(self, n):
        candies = set()
        candies.update(self._generate_candies(self._n_candies[0],
                                              self._mean_candy_sizes[0],
                                              self._candy_size_sdvs[0],
                                              QRectF(0,
                                                   0,
                                                   (self.SIM_WIDTH - self.SEPARATOR_WIDTH) / 2,
                                                   self.SIM_HEIGHT)))
        candies.update(self._generate_candies(self._n_candies[1],
                                              self._mean_candy_sizes[1],
                                              self._candy_size_sdvs[1],
                                              QRectF((self.SIM_WIDTH + self.SEPARATOR_WIDTH)/2,
                                                   0,
                                                   (self.SIM_WIDTH - self.SEPARATOR_WIDTH) / 2,
                                                   self.SIM_HEIGHT)))
        return candies
    
    def _reset_candies(self):
        self._candies.clear()
        for i in range(self._n_candies):
            self._candies.add(Candy.random(mean_size=self._mean_candy_sizes,
                                          sdv=self._candy_size_sdv,
                                          rng=self._rng))
    
    def _random_normal(self, 
                           mean: float,
                           std_dev: float):
        return utils.sample_normal(rng=rng, mean=mean, std_dev=std_dev)

    def _move_blob(self, blob, timediff):
        blob._move(self._candies, self._blobs, self._separators(), timediff)

    def _passive_energy_loss(self, blob, timediff):
        blob.energy -= timediff * blob.PASSIVE_ENERGY_LOSS * blob.traits.size

    def _offspring_position(self, parent: Blob, area: float = 60):
        angle = self._rng.uniform(0, 2*math.pi)
        
        r = math.sqrt(self._rng.uniform(0, area * SIZE_SCALE) / (2 * math.pi))

        center = utils.bound_position(parent.position, utils.radius(area), self._separators())
        
        return QVector2D(x=center.x() + r * math.cos(angle),
                       y=center.y() + r * math.sin(angle))

    def _reproduce(self, blob) -> Sequence[Blob]:
        f = lambda : self._offspring_position(parent=blob, area=60)
        
        if blob.energy / blob.max_energy < 0.5:
            return []
        
        offspring = []
        for _ in range(3):
            blob = Blob.random(rng=self._rng,
                               mean_traits=blob.traits,
                               sdvs=self._mutation_sdvs,
                               separators=self._separators(),
                               gen_position=f)
            blob.position = utils.bound_position(blob.position, blob.radius(), self._separators())
            offspring.append(blob)
        return offspring
        
    def _eat(self, blob: Blob) -> Sequence[Candy]:
        eaten_candies = []
        for candy in self._candies:
            if blob.distance_to(candy) + candy.radius() - blob.radius() <= 2:
                eaten_candies.append(candy)
                blob.energy = min(blob.max_energy,
                                  blob.energy + self._candy_energy_d * candy.size)
        
        return eaten_candies
    
    def _lifecycle_blob(self, blob, timediff) -> tuple[bool, Sequence[Blob]]: 
        dead = False
        offspring = []      
        
        if blob.energy <= 0:
            # print("energyranout")
            dead = True
        
        elif blob.age >= Blob.LIFESPAN:
            if blob.energy / blob.max_energy >= 0.5:
                offspring = self._reproduce(blob)
                
            # print("lifespanexceeded:", blob.energy / blob.max_energy)
            dead = True
        
        return (dead, offspring)
    
    def _spawn_candy(self, timediff):
        for interval in self._intervals:
            x = interval.centerx
            
                
            
            area_ratio = (interval.width * interval.height) / \
                         (self.SIM_WIDTH * self.SIM_HEIGHT)
            int_spawn_rate = self._interpolate(x=x,
                                               range=self._candy_spawn_rates)
            _lambda = int_spawn_rate * timediff * area_ratio
            
            sdv = self._interpolate(x=x,
                                    range=self._candy_size_sdvs)
            
            mean_size = self._interpolate(x=x,
                                    range=self._mean_candy_sizes)

            for _ in range(self._rng.poisson(_lambda)):
                candy = Candy.random(rng=self._rng,
                                    sdv=sdv,
                                    mean_size=mean_size,
                                    bounds=interval)
                if candy != None:
                    candy.position = utils.bound_position(candy.position, candy.radius(), self._separators())
                    
                    self._candies.add(candy)
                    
                    if len(self._candies) > self.CANDY_LIMIT:
                        self._candies.pop()
                    
   
    def _add_blobs(self):
        for blob in self._blobs:
            self.scene.addItem(blob._ellipse)
        
    
    def _add_candies(self):
        for candy in self._candies:
            self.scene.addItem(candy._ellipse)

    
    def _draw_separators(self):
        top, bottom = self._separators()
       
        pygame.draw.rect(self._surface, 0x775002, top)
        pygame.draw.rect(self._surface, 0x775002, bottom)
            
    def _separators(self) -> tuple[QRectF, QRectF]:
        width = self.SEPARATOR_WIDTH
        height = self.SIM_HEIGHT * (1 - self._gap)/2
        return (QRectF(self.SIM_WIDTH/2 - width/2,
                    0,
                    width,
                    height),
                QRectF(self.SIM_WIDTH/2 - width/2,
                    self.SIM_HEIGHT - height,
                    width,
                    height))
       
      