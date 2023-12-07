#! /usr/bin/env python

from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

"""
Used walltime       : 01:04:55
Used CPU time       : 01:04:43 (Efficiency:  1.38%)
Energy (CPU+Mem)    : 0.36kWh (0.15kg CO2, 0.19€)
"""

cores = []
walltime = []
cputime = []
energy = []


def fmtd_time_to_sec(s):
    seconds_in_part = 1
    seconds = 0
    for part in s.split(':')[::-1]:
        seconds += int(part) * seconds_in_part
        seconds_in_part *= 60
    return seconds


def extract_seconds_from_line(line):
    # also remove additional info in parenthesis
    t = line[line.find(':')+2:].split('(')[0]
    t = fmtd_time_to_sec(t)
    return t


def parse_output(run_output):
    run_cores = int(run_output.parent.name)
    with open(run_output, 'r') as f:
        for line in f:
            if line.startswith('Used walltime'):
                run_walltime = extract_seconds_from_line(line)
            elif line.startswith('Used CPU time'):
                run_cputime = extract_seconds_from_line(line)
            elif line.startswith('Energy (CPU+Mem)'):
                run_energy = float(line[line.find(':')+2:].split('kWh')[0])

    cores.append(run_cores)
    walltime.append(run_walltime)
    cputime.append(run_cputime)
    energy.append(run_energy)


for file in Path(__file__).parent.glob('*'):
    if not file.is_dir():
        continue
    parse_output(file/'output')

df = pd.DataFrame({
    'cores': cores,
    'energy': energy,
    'walltime': walltime,
    'cputime': cputime
})

df.sort_values('cores', inplace=True)
print(df.to_csv(index=False))

print('\nCorrelation:')
print(df.corr())

plt.figure()
xcol = 'cores'
i = 0
lns = None
for c in df.columns:
    if c == xcol:
        continue
    if i > 0:
        plt.twinx()
    if c != 'cputime':
        plt.yticks([])
    ln = plt.plot(df[xcol], df[c], label=c, c=f'C{i}')
    if lns is None:
        lns = ln
    else:
        lns += ln
    i += 1
labs = [l.get_label() for l in lns]
plt.xticks(df[xcol])
plt.ylim(0, plt.gca().get_ylim()[1])
plt.show()
