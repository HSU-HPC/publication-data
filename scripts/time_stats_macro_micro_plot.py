#! /usr/bin/env python3

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

plt.rcParams.update({'font.size': 12})

INPUT_FILE = Path(__file__).parent.parent / 'data' / \
    'macro_micro_timestats.csv'
OUTPUT_FILE_BASE_NAME = str(
    Path(__file__).parent.parent / 'figures' / 'macro_micro_timestats')

df = pd.read_csv(INPUT_FILE)

md_sizes = df['md_size'].unique()
rows = 2
cols = len(md_sizes)
# fig, axs = plt.subplots(rows, cols, sharex=True)
# fig.set_size_inches(14, 6)

df_multimd = df[df['runtype'] == 'multimd']
df_filter = df[df['runtype'] == 'filter']
assert (len(df) == len(df_multimd) + len(df_filter))

df = pd.concat([df_multimd, df_filter])
print('Maximum values:')
print(df[['time_percent_macro', 'time_percent_filter']].max())

dfs = [df_multimd, df_filter]
title = ['Multi MD$n', 'Multi MD$n + Filtering']


def plot_stacked_area(df):
    ax = plt.gca()
    base = 0
    col_suffixes = ['other', 'filter', 'macro', 'micro']
    legend_labels = ['Coupling, communication, initialization, $etc.$',
                     'Noise filtering', 'CFD (macro) solver', 'MD (micro) solver']
    for i in range(len(col_suffixes)):
        col_suffix = col_suffixes[i]
        label = legend_labels[i]
        ax.fill_between(df['num_md_sims'], base, base +
                        df[f'time_percent_{col_suffix}'], label=label, edgecolor='k', fc=f'C{len(col_suffixes)-1-i}')
        base += df[f'time_percent_{col_suffix}']
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())


def plot_bars(df):
    col_suffixes = ['other', 'filter', 'macro', 'micro']
    legend_labels = ['Coupling, communication, initialization, $etc.$',
                     'Noise filtering', 'CFD (macro) solver', 'MD (micro) solver']
    nums_md_sims = list(df['num_md_sims'].unique())
    nums_md_sims.sort()
    bar_stack_spacing = 1
    plt.ylim(0, 180)  # Fit legend above 100%
    zoomed_y_portion = 0.4
    y_scale_threshold = 1
    x_max = len(nums_md_sims)*(len(col_suffixes)+bar_stack_spacing)-1
    plt.plot([0, x_max], [y_scale_threshold,
             y_scale_threshold], 'k:', alpha=0.5, zorder=-10)

    def num_md_sims_to_x(num_md_sims, col_idx):
        bar_stack_idx = nums_md_sims.index(num_md_sims)
        bar_stack_width = len(col_suffixes)+bar_stack_spacing
        return bar_stack_idx*bar_stack_width+col_idx

    for i in range(len(col_suffixes)):
        col_suffix = col_suffixes[i]
        label = legend_labels[i]
        for num_md_sims in nums_md_sims:
            y = df[df['num_md_sims'] ==
                   num_md_sims][f'time_percent_{col_suffix}']
            x = num_md_sims_to_x(num_md_sims, i)
            plt.bar(x, y.mean(), edgecolor='k', fc=f'C{len(col_suffixes)-1-i}')
            # Custom error bars
            plt.plot([x,x], [y.mean()-y.std(),y.mean()+y.std()], 'k')
            for y in [y.mean()-y.std(),y.mean()+y.std()]:
                width = 0.25
                plt.plot([x-width/2,x+width/2], [y,y], 'k')
        plt.fill_between([], [], label=label, edgecolor='k',fc=f'C{len(col_suffixes)-1-i}')
    plt.xticks([num_md_sims_to_x(i, (len(col_suffixes)-bar_stack_spacing) / 2)
               for i in nums_md_sims], nums_md_sims)

    def fwd(y):
        y = np.array(y)
        is_over_threshold = np.array(y_scale_threshold < y, dtype=int)
        zoomed = (y/y_scale_threshold) * (zoomed_y_portion * 100) * \
            (1 - is_over_threshold)  # Use as(inverted) flag
        not_zoomed = ((zoomed_y_portion * 100) + (y-1) *
                      (1-zoomed_y_portion)) * is_over_threshold  # Use as flag
        return zoomed + not_zoomed
    plt.gca().set_yscale('function', functions=(fwd, lambda y: y))
    y_ticks = [y_scale_threshold/2, y_scale_threshold, 25, 50, 75, 100]
    plt.yticks(y_ticks, [f'{y}%' for y in y_ticks])


for r in range(rows):
    for c in range(cols):
        df = dfs[r].sort_values(['num_md_sims', 'time_percent_micro'], ascending=[
                                True, True])  # Show full range of values

        # ax.set_title(title[r].replace('$n', str(md_size)))
        runtype = df['runtype'].values[0]
        md_size = md_sizes[c]
        plt.figure(f'Multi MD{md_size} ({runtype})', figsize=(6, 4))
        df = df[df['md_size'] == md_size]
        # plot_stacked_area(df)
        plot_bars(df)
        ax = plt.gca()
        ax.legend(loc='upper left', edgecolor='k', fontsize=10, framealpha=1)
        ax.set_ylabel('Relative wall time')
        ax.set_xlabel('Number of MD instances')

        output_file = f'{OUTPUT_FILE_BASE_NAME}_{md_size}_{runtype}.pdf'
        walltime_sec_mean = int(np.ceil(df["walltime_total_sec"].mean()))
        print(
            f'Exporting MD{md_size} {runtype}\t(mean total walltime = {walltime_sec_mean} sec)\tto {output_file}')
        plt.savefig(output_file)
        # os.system(f'pdfcrop {output_file} {output_file}')

if '--no-show' not in sys.argv:
    plt.show()
