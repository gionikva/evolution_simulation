from classes.game import *

def main():
   game = Game(seed = 10,
               mean_traits=BlobTraits(size=50,
                                      speed=500),
               initial_sdvs=MutationSdvs(size_sdv=10.0,
                                          speed_sdv=0.2),
               mutation_sdvs=MutationSdvs(size_sdv=1.5,
                                          speed_sdv=0.5),
               mean_candy_sizes=(40, 5),
               candy_size_sdvs=(2, 0.1),
               candy_spawn_rates=(10, 100),
               cutoff_sharpness = 4,
               n_candies=(60, 200),
               n_blobs=20,
               candy_energy_density=2000,
               separation_gap=0.8,
               sim_speed=5.)
   game.run()

if __name__ == "__main__":
    main()