#! /usr/bin/env python3

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})

import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import re

from utils import fmt_math_num, r2_score_linear

# Vertical plot range of 0-6kWh for comparison between plots
AX_LIM_kWh=6.5

# Parse script arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', default=None, type=str)
arg_parser.add_argument('input')
args = arg_parser.parse_args()

print(f'\n===== {args.input} =====')

# Load and parse input data
df = pd.read_csv(args.input)
df.drop('filename', axis=1, inplace=True)


def fmtd_duration_to_timedelta(duration_fmtd):
    total_sec = 0
    sec_per_unit = 1
    if '-' in duration_fmtd:
        days = int(duration_fmtd.split('-')[0])
        total_sec += days * (24 * 60 * 60)
    for units_srt in duration_fmtd.split('-')[-1].split(':')[::-1]:
        total_sec += int(units_srt) * sec_per_unit
        sec_per_unit *= 60
    return total_sec

col_wall_time = 'wall_time'
if col_wall_time in df.columns:
    df[col_wall_time] = df[col_wall_time].apply(fmtd_duration_to_timedelta)

col_cpu_time = 'cpu_time'
if col_cpu_time in df.columns:
    df[col_cpu_time] = df[col_cpu_time].apply(fmtd_duration_to_timedelta)
df['md_domain_volume'] = df['md_domain_size'].apply(lambda l: l**3)


def report_correlation(col_a, col_b):
    print(f'{col_a}~{col_b}: {df[col_a].corr(df[col_b])}')


# Create figure
col_energy = 'energy consumption (kWh)'
df.rename(columns={'energy_consumption_kWh': col_energy}, inplace=True)
if col_cpu_time in df.columns:
    col_cpu_time_old = col_cpu_time
    col_cpu_time = 'CPU time (s)'
    df.rename(columns={col_cpu_time_old: col_cpu_time}, inplace=True)

col_mamico_coupling_time_rel = 'MaMiCo coupling overhead'
if 'mamico_coupling_time' in df.columns:
    df[col_mamico_coupling_time_rel] = df['mamico_coupling_time'] / df[col_wall_time]

# Report correlation
if col_cpu_time in df.columns:
    report_correlation(col_energy, col_cpu_time)
    report_correlation('md_domain_volume', col_cpu_time)
report_correlation('md_domain_volume', col_energy)


def plot_column(df, ax, y_col, plot_fit=True, scatter_kwargs={}):
    x = df['md_domain_volume']
    y = df[y_col]
    legend_data = [ax.scatter(x, y, s=100, label=y_col, **scatter_kwargs)]
    ax.set_xlabel('MD domain volume')
    y_col_fmtd = y_col[0].upper() + y_col[1:]
    ax.set_ylabel(y_col_fmtd)
    m, c = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
    r2 = r2_score_linear(x, y, m, c)
    print(f'fit {y_col}: {m:.3}x+{c:.3} (r2={r2:.5})')
    if plot_fit:
        legend_data += ax.plot(
            x, m*x+c, 'k-', label=f'{y_col_fmtd} fit: $y={fmt_math_num(m)}x+{fmt_math_num(c)}$')
    return legend_data


plt.figure()
ax = plt.gca()
legend_data = plot_column(df, ax, col_energy, scatter_kwargs={
                          'marker': '.', 'c': 'k'})
ax.set_ylim([0,AX_LIM_kWh])

if col_mamico_coupling_time_rel in df.columns:
    # Add invisible right ticks and axis label so all figures have the same width
    ax = ax.twinx()
    # legend_data += plot_column(df.dropna(), ax, col_mamico_coupling_time_rel, False, {'marker': 'D', 'c': 'none', 'edgecolor': 'k'})
    legend_data += ax.plot(df.dropna()['md_domain_volume'], df.dropna()[col_mamico_coupling_time_rel], 'k--D', label=col_mamico_coupling_time_rel, markersize=10, mfc='w')
    ax.set_ylim([0,1])
    ax.set_ylabel('Relative wall time')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
elif col_cpu_time in df.columns:
    ax = ax.twinx()
    legend_data += plot_column(df, ax, col_cpu_time, False, {
        'marker': 'D', 'c': 'none', 'edgecolor': 'k'})
legend_labels = [re.compile(r'\s+\(.*\)').sub('', l.get_label())  # Remove additional details
                 for l in legend_data]
ax.legend(legend_data, legend_labels, loc='upper left', edgecolor='k', fontsize=10)

x_tick_labels = [f'${x}^3$' if x >=
                 120 else '' for x in sorted(df['md_domain_size'].unique())]
x_ticks = sorted(df['md_domain_volume'].unique())
ax.set_xticks(x_ticks, x_tick_labels)
plt.gcf().tight_layout()
plt.gcf().set_size_inches(12, 4)

# Output visualization
if args.output is not None:
    plt.savefig(args.output)
else:
    plt.show()
