#! /usr/bin/env python3

import matplotlib.pyplot as plt
import argparse

import pandas as pd

from utils import r2_score_linear

plt.rcParams.update({'font.size': 12})


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', default=None, type=str)
arg_parser.add_argument('--md60', default=None, type=str)
arg_parser.add_argument('--md120', default=None, type=str)
arg_parser.add_argument('--md180', default=None, type=str)
args = arg_parser.parse_args()

plt.figure()

# Load all data
dfs = {}
if args.md60 is not None:
    dfs['MD60'] = pd.read_csv(args.md60)
if args.md120 is not None:
    dfs['MD120'] = pd.read_csv(args.md120)
if args.md180 is not None:
    dfs['MD180'] = pd.read_csv(args.md180)

print(f'\n===== {list(dfs.keys())} =====')

# Plot all loaded data
plot_styles = ['k-o', 'k--D', 'k:s']
for i, (k, df) in enumerate(dfs.items()):
    x = df['num_md_sims']
    y = df['abs_vel_error']
    plt.plot(x, y,
             plot_styles[i], mfc='w', label=k)
plt.xlabel('Number of MD Instances')
plt.ylabel('Absolute Velocity Error')
plt.gca().set_yscale('log')
plt.gca().set_xscale('log')
plt.legend(edgecolor='k')

# Output visualization
if args.output is not None:
    plt.savefig(args.output)
else:
    plt.show()
