#!/bin/bash

#SBATCH --time=03:00:00
#SBATCH --nodes=64
#SBATCH --ntasks-per-node=72
#SBATCH --cpus-per-task=1
#SBATCH --partition=medium
#SBATCH --job-name="mamico_verify"
#SBATCH --output="output"

ml mpi/2021.6.0

export OMP_NUM_THREADS=1

cd <REDACTED>/configurations/verification_runs/V160/M144_stacked
srun <REDACTED>/MaMiCo/build/couette
