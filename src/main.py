from classes.game import *

def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=60,
                                      speed=500),
               initial_sdvs=MutationSdvs(size_sdv=20.0,
                                          speed_sdv=0.2),
               mutation_sdvs=MutationSdvs(size_sdv=1.5,
                                          speed_sdv=0.5),
               mean_candy_sizes=(30, 7),
               candy_size_sdvs=(10, 2),
               candy_spawn_rates=(30, 100),
               cutoff_sharpness = 10,
               n_candies=(60, 200),
               n_blobs=60,
               candy_energy_density=2000,
               separation_gap=1,
               sim_speed=2.)
   game.run()

if __name__ == "__main__":
    main()