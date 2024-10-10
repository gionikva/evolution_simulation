import pygame
from classes.blob import *
from classes.candy import Candy
from numpy import random



class Game():
    SCREEN_WIDTH=1200
    SCREEN_HEIGHT=1200
    BLOB_COLOR = (100, 100, 255)
    CANDY_COLOR = (146, 77, 155)
    def __init__(self, *,
                # Rng seed
                seed = None,
                        
                # Mean trait values for the starting population
                mean_traits = BlobTraits(size = 20.0,
                                         speed = 5.0),
                
                # Mean candy size
                mean_candy_size = 5.0,
                
                # Mutation standard deviation
                mutation_sdvs = MutationSdvs(size_sdv = 5,
                                             speed_sdv = 2),
                
                # Candy size standard deviation
                candy_size_sdv = 2.0,
                        
                # Starting number of blobs
                n_blobs = 10,
                
                # Starting number of candy
                n_candies = 20,):

        self.seed = seed
        self.mean_traits = mean_traits
        self.mean_candy_size = mean_candy_size
        self.mutation_sdvs = mutation_sdvs
        self.candy_size_sdv = candy_size_sdv
        
        self.rng = random.default_rng(seed=seed)
        
        
        self.blobs = self._gen_initial_blobs(n_blobs)
        self.candies = self._gen_initial_candies(n_candies)
        
        
        
  
    
    def _gen_initial_blobs(self, n):
        blobs = set()
        for i in range(n):
            size = self._get_random_normal(mean=self.mean_traits.size,
                                           std_dev=self.mutation_sdvs.size)
            
            speed = self._get_random_normal(mean=self.mean_traits.speed,
                                           std_dev=self.mutation_sdvs.speed)
            
            position = (self.rng.uniform(size / 2, self.SCREEN_WIDTH - size / 2),
                        self.rng.uniform(size / 2, self.SCREEN_HEIGHT - size / 2))
            
            blobs.add(Blob.from_traits(size, speed, position))
        return blobs
    
    def _gen_initial_candies(self, n):
        candies = set()
        for i in range(n):
            size = self._get_random_normal(mean=self.mean_candy_size,
                                           std_dev=self.candy_size_sdv)
            
            position = (self.rng.uniform(size / 2, self.SCREEN_WIDTH - size / 2),
                        self.rng.uniform(size / 2, self.SCREEN_HEIGHT - size / 2))
            
            candies.add(Candy(size=size,
                              position=position))
        return candies
    
    def _gen_intial_candies(self, n):
        pass
    
    def _get_random_normal(self, 
                           mean: float,
                           std_dev: float):
        return self.rng.normal() * std_dev + mean
    
    def _draw_blob(self, blob: Blob):
        pygame.draw.circle(self.screen,
                           self.BLOB_COLOR,
                           blob.position,
                           blob.traits.size)
        
    def _draw_blobs(self):
        for blob in self.blobs:
            self._draw_blob(blob)
            
    def _draw_candy(self, candy: Candy):
         pygame.draw.circle(self.screen,
                            self.CANDY_COLOR,
                            candy.position,
                            candy.size)
    
    def _draw_candies(self):
        for candy in self.candies:
            self._draw_candy(candy)
    
            
    def _draw(self):
        self._draw_candies()
        self._draw_blobs()
    
    def run(self):
        pygame.init()
      

        # Set up the drawing window

        self.screen = pygame.display.set_mode([self.SCREEN_WIDTH,
                                          self.SCREEN_HEIGHT])


        # Run until the user asks to quit

        running = True

        while running:


            # Did the user click the window close button?

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False


            # Fill the background with white

            self.screen.fill((255, 255, 255))


            # Draw a solid blue circle in the center
            
            self._draw()
            
            #pygame.draw.circle(self.screen, (0, 0, 255), (250, 250), 75)


            # Flip the display

            pygame.display.flip()


        # Done! Time to quit.

        pygame.quit()


def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=20,
                                      speed=5),
               mutation_sdvs=MutationSdvs(size_sdv=2.0,
                                          speed_sdv=0.2),
               mean_candy_size=10,
               candy_size_sdv=0.3)
   game.run()

if __name__ == "__main__":
    main()