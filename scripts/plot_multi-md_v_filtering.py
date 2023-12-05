#! /usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import partial

from utils import r2_score_linear
plt.rcParams.update({'font.size': 12})

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', default=None, type=str)
arg_parser.add_argument('--md60', default=None, type=str)
arg_parser.add_argument('--md120', default=None, type=str)
arg_parser.add_argument('--md180', default=None, type=str)
arg_parser.add_argument('-c','--column', choices=['energy', 'snr_gain'], required=True)
args = arg_parser.parse_args()

# Load all data
dfs_md_sizes = {}
if args.md60 is not None:
    dfs_md_sizes['MD60'] = pd.read_csv(args.md60)

if args.md120 is not None:
    dfs_md_sizes['MD120'] = pd.read_csv(args.md120)
if args.md180 is not None:
    dfs_md_sizes['MD180'] = pd.read_csv(args.md180)

print(f'\n===== {list(dfs_md_sizes.keys())} - {args.column} =====')

for j,(k,df) in enumerate(dfs_md_sizes.items()):
    df_multimd = df[df['runtype'] == 'multimd']
    df_filter = df[df['runtype'] == 'filter']
    dfs = [df_multimd, df_filter]

    # fig, axs = plt.subplots(1, 2)
    # fig.set_size_inches(12, 4)
    fig = plt.figure(f'{k} {args.column}')
    ax = plt.gca()


    x = df_multimd['num_md_sims']
    for _x, _y in zip(x, dfs[0][f'avg_{args.column}']):
        width = 5
        ax.fill_between(x, dfs[0][f'min_{args.column}'], dfs[0][f'max_{args.column}'], fc=f'C{j}', alpha=0.025)
    ax.plot(x, dfs[0][f'avg_{args.column}'], f'C{j}--', marker='x')
    ax.plot([],[],f'C{j}--x', label=f'{k}')

    df = dfs[1]
    x = df['num_md_sims']
    y = df[f'avg_{args.column}']

    ax.fill_between(x, df[f'min_{args.column}'], df[f'max_{args.column}'], fc=f'C{j}', alpha=0.5)
    err = (df[f'max_{args.column}'] - df[f'min_{args.column}']) / 2
    # ax.errorbar(x, y, yerr=err, c=f'C{j}') # FIXME: Not completely correct, because yerr is not symmetrical sometimes
    ax.plot(x, y, f'C{j}-', marker='.', label=f'{k} + Filtering', zorder=10)
    ax.set_xlabel('Number of MD instances')

    ax.legend(edgecolor=f'k', framealpha=1, loc='lower right')

    if args.column == 'energy':
        ylabel = 'Energy consumption (kWh)'
    else:
        ylabel = 'SNR gain (dB)'
        # ax.yaxis.tick_right()
        # ax.yaxis.set_label_position("right")
    y_max = np.max([df[f'max_{args.column}'].max() for df in dfs]) + 1
    ax.set_ylabel(ylabel)
    ax.set_ylim((-1, y_max))

    # Output visualization
    if args.output is not None:
        idx_suffix_sep = args.output.rindex('.')
        base_filename = args.output[:idx_suffix_sep]
        suffix = args.output[idx_suffix_sep:]
        plt.savefig(f'{base_filename}_{k}{suffix}')
    else:
        plt.show()

print()
