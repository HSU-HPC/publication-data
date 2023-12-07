# The Error-Energy Tradeoff in Molecular and Molecular-Continuum Fluid Simulation
_Amartya Das Sharma, Ruben Horn, Philipp Neumann: Helmut Schmidt University, Hamburg, Germany_

This repository contains the replication package (configuration, generated output, post-processing and visualization scripts) associated with our manuscript **The Error-Energy Tradeoff in Molecular and Molecular-Continuum Fluid Simulation**, submitted to the workshop "Multi-scale, Multi-physics and Coupled Problems on highly parallel systems (MMCP)" at HPC Asia 2024.


### Contents:
| Folder | Description |
|---|---|
|`raw_data/`|Input and output of the experiments, job scripts and some small post processing scripts run on the cluster (for a list of all scripts run `find raw_data/ -name '*.py'`)|
|`data/`|Data aggregated and processed manually or usings scripts from `raw_data/`|
|`figures/`|Visualizations of `data/`|
|`scripts/`|Python3 script to generate files in `data/` and `figures`|

### Software
+ [ls1 mardyn](https://github.com/ls1mardyn/ls1-mardyn/tree/baca393d7)
+ [MaMiCo](https://github.com/HSU-HPC/MaMiCo/tree/3e516cc3) with [ls1 mardyn for coupling](https://github.com/ls1mardyn/ls1-mardyn/tree/31e1e4819)
+ Slurm workload manager with [jobinfo](https://github.com/birc-aeh/slurm-utils/tree/master) running on the [HSUper cluster](https://www.hsu-hh.de/hpc/en/hsuper/) to execute the experiments and measure energy consumption using [RAPL](https://github.com/SchedMD/slurm/blob/master/src/plugins/acct_gather_energy/rapl/acct_gather_energy_rapl.c)

### Basic usage
Requirements can be installed with `pip3 install -r requirements.txt`.  
Use `./run_all.sh | tee run_all_out.txt` to (re-)generate most output (figures and report including analysis results from stdout).

