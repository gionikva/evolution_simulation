from classes.game import *

def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=40,
                                      speed=500),
               initial_sdvs=MutationSdvs(size_sdv=10.0,
                                          speed_sdv=0.2),
               mutation_sdvs=MutationSdvs(size_sdv=1.5,
                                          speed_sdv=0.5),
               mean_candy_sizes=(10, 10),
               candy_size_sdvs=(5, 5),
               candy_spawn_rates=(100, 100),
               n_candies=(60, 60),
               n_blobs=15,
               candy_energy_density=3200,
               separation_gap=0.5,
               sim_speed=5.)
   game.run()

if __name__ == "__main__":
    main()