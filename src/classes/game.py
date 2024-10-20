import pygame
from pygame.time import Clock
from pygame import Rect
from classes.blob import *
from classes.candy import Candy
from classes.constants import SIZE_SCALE, SIM_WIDTH, SIM_HEIGHT
import math
from numpy import random



class Game():
    SIM_WIDTH=SIM_WIDTH
    SIM_HEIGHT=SIM_HEIGHT
    STATBAR_HEIGHT = 100
    SEPARATOR_WIDTH = 50
    
    N_INTERVALS = 40

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
                                         speed = 5.0),
                
                # Mean candy size
                mean_candy_sizes: tuple[float, float] = (5.0, 5.0),
                
                # Mutation standard deviation
                mutation_sdvs: MutationSdvs = MutationSdvs(size_sdv = 5,
                                             speed_sdv = 2),
                initial_sdvs: MutationSdvs = MutationSdvs(size_sdv = 5,
                                             speed_sdv = 2),
                
                # Candy size standard deviation
                candy_size_sdvs: tuple[float, float] = (2.0, 2.0),
                
                # Energy a candy provides when \
                # eaten per unit size.
                candy_energy_density: float = 2000,
                
                cutoff_sharpness: float = 2,
                        
                # Starting number of blobs
                n_blobs: int = 10,
                
                # Starting number of candy
                n_candies: tuple[int, int] = (20, 20),
                candy_spawn_rates: tuple[float, float] = (10, 10),
                separation_gap: float = 0,
                sim_speed: float = 1,
                ):

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
            return
        
        dist = blob.distance_to(candy)
        blob.acc = Blob.ACC_MULTIPLIER * Vector2(candy.position.x - blob.position.x,
                            candy.position.y - blob.position.y) / dist
        # self._acc -= self._vel * self.FRICTION 
        blob.vel += blob.acc * timediff
        if blob.vel.magnitude() > blob.traits.speed:
            blob.vel = blob.vel * blob.traits.speed / blob.vel.magnitude()
        # self._vel = min(self._vel, self.traits.speed)
        
        movement = (blob.vel + 0.3 * blob.acc) * timediff
                

        oldpos = blob.position
        
        blob.position = self._bound_position(blob.position + movement, blob.radius())

        movement = blob.position - oldpos
            
        blob.energy -= (Blob.ENERGY_EXP_SIZE_R * blob.traits.size) * movement.magnitude() * \
            Blob.VEL_ENERGY_MULT * blob.vel.magnitude()

    def _passive_energy_loss(self, blob, timediff):
        blob.energy -= timediff * blob.PASSIVE_ENERGY_LOSS * blob.traits.size

    def _offspring_position(self, parent: Blob, area: float = 60):
        angle = self._rng.uniform(0, 2*math.pi)
        r = math.sqrt(self._rng.uniform(0, area * SIZE_SCALE) / (2 * math.pi))
        return Vector2(x=parent.position.x + r * math.cos(angle),
                       y=parent.position.y + r * math.sin(angle))

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
            if blob.distance_to(candy) + candy.radius() - blob.radius() <= 0.001:
                eaten_candies.append(candy)
                blob.energy = min(blob.max_energy,
                                  blob.energy + self._candy_energy_d * candy.size)
        
        return eaten_candies
    
    def _lifecycle_blob(self, blob, timediff) -> tuple[bool, Sequence[Blob]]: 
        dead = False
        offspring = []      
        
        if blob.energy <= 0:
            print("energyranout")
            dead = True
        
        elif blob.age >= Blob.LIFESPAN:
            if blob.energy / blob.max_energy >= 0.5:
                offspring = self._reproduce(blob)
                
            print("lifespanexceeded:", blob.energy / blob.max_energy)
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
                candy.position = self._bound_position(candy.position, candy.radius())
                
                self._candies.add(candy)
                
                if len(self._candies) > self.CANDY_LIMIT:
                    self._candies.pop()
        
    def on_loop(self):
        timediff = self._sim_speed * self._loop_clock.tick() / 1000
        
        deadblobs = []
        newblobs = []
        
        for blob in self._blobs:
            self._move_blob(blob, timediff)
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
    
    # TODO: Fix bug of candies spawning inside the separators
    
    def _draw(self):
        self._draw_candies()
        self._draw_blobs()
        self._draw_separators()
        
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
                            print("ticked,", self._loop_clock.tick())

            
            self.screen.fill((255, 255, 255))
            pygame.draw.rect(self.screen, (0, 0, 0), Rect(0, SIM_HEIGHT-1, SIM_WIDTH, 5))
            self._draw()

            pygame.display.flip()
        
        pygame.quit()
