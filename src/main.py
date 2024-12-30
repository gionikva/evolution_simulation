from classes.game import *
import sys
import os.path

def main():
   game = Game.from_config(open("./config.json"))
   # game = Game(
   #             seed = 10,
   #             mean_traits=BlobTraits(size=30,
   #                                    speed=200),
   #             initial_sdvs=MutationSdvs(size_sdv=0.0,
   #                                        speed_sdv=0.2),
   #             mutation_sdvs=MutationSdvs(size_sdv=1.5,
   #                                        speed_sdv=25),
   #             mean_candy_sizes=(20, 10),
   #             candy_size_sdvs=(2, 1),
   #             candy_spawn_rates=(20, 90),
   #             cutoff_sharpness = 10,
   #             n_candies=(60, 200),
   #             n_blobs=40,
   #             candy_energy_density=2300,
   #             separation_gap=0.0,
   #             sim_speed=5.
   #             )
   game.run()
   
if __name__ == "__main__":
    main()