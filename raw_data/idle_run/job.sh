#!/bin/bash

#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=72
#SBATCH --cpus-per-task=1
#SBATCH --partition=small
#SBATCH --job-name="idle_job"
#SBATCH --output="output"

cd <REDACTED>/configurations/idle_run
sleep 734
