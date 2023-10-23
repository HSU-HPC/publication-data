#!/bin/bash

#SBATCH --time=00:40:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --cpus-per-task=1
#SBATCH --partition=small
#SBATCH --job-name="mamico_verify"
#SBATCH --output="output"

ml mpi/2021.6.0

export OMP_NUM_THREADS=1

cd <REDACTED>/configurations/verification_runs/V80/M1
srun <REDACTED>/MaMiCo/build/couette
