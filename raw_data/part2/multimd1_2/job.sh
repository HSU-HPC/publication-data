#!/bin/bash

#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=72
#SBATCH --cpus-per-task=1
#SBATCH --partition=small
#SBATCH --job-name="mamico_scale"
#SBATCH --output="output"

ml mpi/2021.6.0

export OMP_NUM_THREADS=1

cd <REDACTED>/configurations/part2/multimd1_2
srun <REDACTED>/MaMiCo/build/couette
