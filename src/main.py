from classes.game import *

def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=40,
                                      speed=500),
               initial_sdvs=MutationSdvs(size_sdv=10.0,
                                          speed_sdv=0.2),
               mutation_sdvs=MutationSdvs(size_sdv=1.5,
                                          speed_sdv=0.5),
               mean_candy_size=10,
               candy_size_sdv=5,
               n_candies=125,
               n_blobs=15,
               candy_energy_density=3200,
               candy_spawn_rate=100.,
               separation_gap=0.5,
               sim_speed=5.)
   game.run()

if __name__ == "__main__":
    main()