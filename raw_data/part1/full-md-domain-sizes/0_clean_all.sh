#! /bin/bash

cd "$(dirname "$0")"

rm -f *.dat # Checkpoints
rm -f *.xml # ls1 config files
rm -f *.job # Slurm job scripts
rm -f *.log # Slurm job logs
rm -f *.csv # Final data aggregate
