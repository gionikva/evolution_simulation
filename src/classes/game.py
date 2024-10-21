import json
import pygame
from typing import Self, IO
from pygame.time import Clock
from pygame.font import Font
from pygame import Rect
from classes.blob import *
from classes.candy import Candy
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT
import math
from numpy import random



class Game():
    SIM_WIDTH=SIM_WIDTH
    SIM_HEIGHT=SIM_HEIGHT
    STATBAR_HEIGHT = 180
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
                sim_speed: float = 1,
                ):

        pygame.font.init()

        self._seed = seed
        self._mean_traits = BlobTraits(size=mean_traits.size,
                                      speed=mean_traits.speed)
        self._mutation_sdvs = MutationSdvs(size_sdv=mutation_sdvs.size,
                                          speed_sdv=mutation_sdvs.speed)
        self._initial_sdvs = initial_sdvs
        self._candy_energy_d = candy_energy_density
        
        self._rng = random.default_rng(seed=seed)
        self._loop_clock = Clock()
        
        self._gap = separation_gap
        self._sim_speed = sim_speed
    
        self._mean_candy_sizes = mean_candy_sizes
        self._candy_size_sdvs = candy_size_sdvs
        self._candy_spawn_rates = candy_spawn_rates
        self._n_candies = n_candies
        self._cutoff_sharpness = cutoff_sharpness
        
        self._intervals: list[Rect] = self._gen_intervals()
        
        self._candies = self._gen_initial_candies(n_candies)
        self._blobs = self._gen_initial_blobs(n_blobs)
        
        self._paused_clock = Clock()
        self._paused_time = 0
        
    def from_config(file: IO) -> Self:
        config: dict = json.load(file)
        return Game(
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
    
    def _gen_interval(self, i: int) -> Rect:
        left = self._interval_width() * i
        width = self._interval_width()
        rect = Rect(left,
                     0, 
                     width,
                     self.SIM_HEIGHT)
        
        separators = self._separators()
        
        if rect.collidelist(separators) != -1:
            rect = Rect(left,
                         separators[0].bottom,
                         width,
                         self._gap * self.SIM_HEIGHT)
        
        return rect
    
    def _gen_intervals(self) -> list[Rect]:
        return [self._gen_interval(i) for i in range(self.N_INTERVALS)]
            
    
    def _radius(self, size: float) -> float:
        return math.sqrt(size * SIZE_SCALE / (2 * math.pi))
        
    def _gen_initial_blobs(self, n):
        blobs = set()
        for i in range(n):
            blob = Blob.random(mean_traits=self._mean_traits,
                                  sdvs=self._initial_sdvs,
                                  rng=self._rng)
            blob.position = self._bound_position(blob.position, blob.radius())
            blobs.add(blob)
        return blobs
    
   
    def _generate_candies(self, n: int,
                          mean_size: float,
                          sdv: float,
                          region: Rect) -> list[Candy]:
        candies = []
        for i in range(n):
            candy = Candy.random(mean_size=mean_size,
                                     sdv=sdv,
                                     rng=self._rng,
                                     bounds=region)
            candy.position = self._bound_position(candy.position, candy.radius())
            candies.append(candy)
        return candies
    
    def _gen_initial_candies(self, n):
        candies = set()
        candies.update(self._generate_candies(self._n_candies[0],
                                              self._mean_candy_sizes[0],
                                              self._candy_size_sdvs[0],
                                              Rect(0,
                                                   0,
                                                   (self.SIM_WIDTH - self.SEPARATOR_WIDTH) / 2,
                                                   self.SIM_HEIGHT)))
        candies.update(self._generate_candies(self._n_candies[1],
                                              self._mean_candy_sizes[1],
                                              self._candy_size_sdvs[1],
                                              Rect((self.SIM_WIDTH + self.SEPARATOR_WIDTH)/2,
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
    
    def _abs_time(self):
        return time.get_ticks() / 1000 - self._paused_time
    
    def _time(self):
        return self._sim_speed * self._abs_time()
    
    
    def _rect_intersect(self, position: Vector2, radius: float, rect: Rect) -> tuple[bool, Vector2]:
        cleft, cright = (position.x - radius, position.x + radius)
        ctop, cbottom = (position.y - radius, position.y + radius)
        
       
            
        # crect = Rect(cleft, ctop, radius*2, radius*2)
        
        if rect.top <= position.y <= rect.bottom:
            if cright > rect.left and cleft < rect.left:
                return (True, Vector2(rect.left - radius, position.y))
            
            if cleft < rect.right and cright > rect.right:
                return (True, Vector2(rect.right + radius, position.y))
    
        if rect.left <= position.x <= rect.right:
            if ctop < rect.bottom and cbottom > rect.bottom:
                return (True, Vector2(position.x, rect.bottom + radius))
            
            if cbottom > rect.top and ctop < rect.top:
                return (True, Vector2(position.x, rect.top - radius))
            
        for corner in [rect.bottomleft, rect.bottomright, rect.topleft, rect.topright]:
            dist = math.sqrt((corner[0] - position.x)**2 + (corner[1]-position.y)**2)
            if dist < radius:
                s = Vector2(corner[0] - position.x, corner[1] - position.y)
                r = (s / s.magnitude()) * radius
                m = s - r
                return (True, position + m)
                    
        return (False, None)
    

    def _bound_position(self, position: Vector2, radius: float):
        
        pos: Vector2 = utils.bound_position(position, radius)[0]
        
        # Check if blob intersects with separator
      
        
        top, bottom = self._separators()
        
        for rect in [top, bottom]:
            _, newpos = self._rect_intersect(pos, radius, rect)
            if newpos != None:
                pos = newpos
                
        return pos

    def _move_blob(self, blob, timediff):
        def visible(candy: Candy) -> bool:
            for sep in self._separators():
                if sep.clipline((blob.position.x, blob.position.y),
                                (candy.position.x, candy.position.y)) != ():
                    # print(sep.clipline((blob.position.x, blob.position.y),
                    #             (candy.position.x, candy.position.y)), candy)
                    return False
            return True
        
        candy = blob.closest_candy(self._candies, visible)
        if candy == None:
            # print("INVISIBLE")
            return
        
        dist = blob.distance_to(candy)
        displacement = Vector2(candy.position.x - blob.position.x,
                            candy.position.y - blob.position.y)
        
        
        # New (basic) movement logic
        # d_norm = displacement / displacement.magnitude()
        
        # blob.vel = d_norm * blob.traits.speed
        
        # movement = blob.vel * timediff
        
        # Old movement logic
        
        blob.acc = Blob.ACC_MULTIPLIER * displacement / dist
        # self._acc -= self._vel * self.FRICTION 
        blob.vel += blob.acc * timediff
        
        
       
        
        if blob.vel.magnitude() > blob.traits.speed:
            blob.vel = blob.vel * blob.traits.speed / blob.vel.magnitude()
        # self._vel = min(self._vel, self.traits.speed)
        
        fvel = blob.vel + 0.2 * blob.acc
        
        if fvel.magnitude() > blob.traits.speed:
            fvel = fvel * blob.traits.speed / fvel.magnitude()
        
        movement = fvel * timediff
                

        oldpos = blob.position
        
        blob.position = self._bound_position(blob.position + movement, blob.radius())

        movement = blob.position - oldpos
        
        # slope = movement.y / movement.x
        
        
            
        blob.energy -= (Blob.ENERGY_EXP_SIZE_R * blob.traits.size) * movement.magnitude() * \
            (1 + Blob.VEL_ENERGY_MULT * blob.vel.magnitude())

    def _passive_energy_loss(self, blob, timediff):
        blob.energy -= timediff * blob.PASSIVE_ENERGY_LOSS * blob.traits.size

    def _offspring_position(self, parent: Blob, area: float = 60):
        angle = self._rng.uniform(0, 2*math.pi)
        
        r = math.sqrt(self._rng.uniform(0, area * SIZE_SCALE) / (2 * math.pi))

        center = self._bound_position(parent.position, utils.radius(area))
        
        return Vector2(x=center.x + r * math.cos(angle),
                       y=center.y + r * math.sin(angle))

    def _reproduce(self, blob) -> Sequence[Blob]:
        f = lambda : self._offspring_position(parent=blob, area=60)
        
        if blob.energy / blob.max_energy < 0.5:
            return []
        
        offspring = []
        for _ in range(3):
            blob = Blob.random(rng=self._rng, mean_traits=blob.traits, sdvs=self._mutation_sdvs, gen_position=f)
            blob.position = self._bound_position(blob.position, blob.radius())
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
                    candy.position = self._bound_position(candy.position, candy.radius())
                    
                    self._candies.add(candy)
                    
                    if len(self._candies) > self.CANDY_LIMIT:
                        self._candies.pop()
                    
    def _calculate_mean_traits(self) -> tuple[BlobTraits, BlobTraits]:
        leftsums = BlobTraits(size=0., speed=0.)
        rightsums = BlobTraits(size=0., speed=0.)
        
        nleft = 0
        nright = 0
        
        for blob in self._blobs:
            if blob.position.x < SIM_WIDTH / 2:
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
                
    def on_loop(self):
        timediff = self._sim_speed * self._loop_clock.tick() / 1000
        
        deadblobs = []
        newblobs = []
        
        for blob in self._blobs:
            eaten_candies =  self._move_blob(blob, timediff)
            self._passive_energy_loss(blob, timediff)
            blob.age_by(timediff)
            dead, offspring = self._lifecycle_blob(blob, timediff)
            
            if dead:
                deadblobs.append(blob)
            
            newblobs.extend(offspring)
            
            eaten_candies = self._eat(blob)
            
            for eaten in eaten_candies:
                self._candies.remove(eaten)           
          
        for blob in deadblobs:
            if blob in self._blobs:
                self._blobs.remove(blob)
        
        for blob in newblobs:
            self._blobs.add(blob)
            
        self._spawn_candy(timediff)
      
    
    
    def _draw_blob(self, blob: Blob):
        pygame.draw.circle(self.screen,
                           blob.color,
                           blob.position,
                           blob.radius())
        
    def _draw_blobs(self):
        for blob in self._blobs:
            self._draw_blob(blob)
            
    def _draw_candy(self, candy: Candy):
         pygame.draw.circle(self.screen,
                            self.CANDY_COLOR,
                            candy.position,
                            candy.radius())
    
    def _draw_candies(self):
        for candy in self._candies:
            self._draw_candy(candy)

    
    def _draw_separators(self):
        top, bottom = self._separators()
       
        pygame.draw.rect(self.screen, 0x775002, top)
        pygame.draw.rect(self.screen, 0x775002, bottom)
    
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
            

    
    def _draw_statbar(self):
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(0, SIM_HEIGHT-1, SIM_WIDTH, 5))
        pygame.draw.line(self.screen, (0, 0, 0), (SIM_WIDTH/2, SIM_HEIGHT),
                         (SIM_WIDTH/2, SIM_HEIGHT + self.STATBAR_HEIGHT),
                         5)
        
        lmean, rmean = self._calculate_mean_traits()
        
        self._draw_trait_values(position=(20, SIM_HEIGHT + 20),
                                mean_size=lmean.size,
                                mean_speed=lmean.speed,
                                alignleft=True)
        self._draw_trait_values(position=(SIM_WIDTH / 2 + 20, SIM_HEIGHT + 20),
                                mean_size=rmean.size,
                                mean_speed=rmean.speed,
                                alignleft=True)
    
    # TODO: Fix bug of candies spawning inside the separators
    
    def _draw(self):
        self._draw_candies()
        self._draw_blobs()
        self._draw_separators()
        self._draw_statbar()
        
    def _separators(self) -> tuple[Rect, Rect]:
        width = self.SEPARATOR_WIDTH
        height = self.SIM_HEIGHT * (1 - self._gap)/2
        return (Rect(self.SIM_WIDTH/2 - width/2,
                    0,
                    width,
                    height),
                Rect(self.SIM_WIDTH/2 - width/2,
                    self.SIM_HEIGHT - height,
                    width,
                    height))
        
    def _move(self, blob: Blob, candy: Candy):
        pass
    
    def run(self):
        pygame.init()

        self.screen = pygame.display.set_mode([self.SIM_WIDTH,
                                          self.SIM_HEIGHT+self.STATBAR_HEIGHT])

        self._loop_clock.tick()
        self._paused_clock.tick()
                
        running = True
        paused = False

        while running:
            if not paused:
                self.on_loop()
            else:
                self._paused_time += self._paused_clock.tick() / 1000

            pressed_keys = pygame.key.get_pressed()
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                        if paused:
                            self._paused_clock.tick()
                        else:
                            self._loop_clock.tick()

            
            self.screen.fill((255, 255, 255))
            
            self._draw()

            pygame.display.flip()
        
        pygame.quit()
