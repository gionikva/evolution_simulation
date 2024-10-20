from classes.game import *

def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=40,
                                      speed=500),
               initial_sdvs=MutationSdvs(size_sdv=10.0,
                                          speed_sdv=0.2),
               mutation_sdvs=MutationSdvs(size_sdv=1.5,
                                          speed_sdv=0.5),
               mean_candy_sizes=(20, 8),
               candy_size_sdvs=(2, 1),
               candy_spawn_rates=(50, 80),
               n_candies=(60, 600),
               n_blobs=10,
               candy_energy_density=3200,
               separation_gap=0.0,
               sim_speed=1.)
   game.run()

if __name__ == "__main__":
    main()