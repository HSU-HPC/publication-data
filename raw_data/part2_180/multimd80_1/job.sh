#!/bin/bash

#SBATCH --time=02:30:00
#SBATCH --nodes=80
#SBATCH --ntasks-per-node=72
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --job-name="mamico_scale"
#SBATCH --output="output"

ml mpi/2021.6.0

export OMP_NUM_THREADS=1

cd <REDACTED>/configurations/part2_180/multimd80_1
srun <REDACTED>/MaMiCo/build/couette
