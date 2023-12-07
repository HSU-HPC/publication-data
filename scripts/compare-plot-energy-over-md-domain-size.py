#! /usr/bin/env python3

from utils import r2_score_linear, update_axis_ticks_md_volume
import pandas as pd
import numpy as np
import matplotlib.transforms as mtransforms
import matplotlib.ticker as mtick
import argparse
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})


# Parse script arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', default=None, type=str)
arg_parser.add_argument('--fmd', required=True)
arg_parser.add_argument('--cpld', required=True)
args = arg_parser.parse_args()

print(f'\n===== {args.fmd} (MD) vs {args.cpld} (Coupled) =====')

# Load and parse input data
df_fmd = pd.read_csv(args.fmd)
df_cpld = pd.read_csv(args.cpld)


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
col_cpu_time = 'CPU time (s)'
col_energy = 'energy consumption (kWh)'
col_mamico_coupling_time_abs = 'mamico_coupling_time'

# Pre-process input data
for df in [df_fmd, df_cpld]:
    # Rename columns
    df.rename(columns={'cpu_time': col_cpu_time}, inplace=True)
    df.rename(columns={'energy_consumption_kWh': col_energy}, inplace=True)

    df[col_wall_time] = df[col_wall_time].apply(fmtd_duration_to_timedelta)
    df[col_cpu_time] = df[col_cpu_time].apply(fmtd_duration_to_timedelta)
    df['md_domain_volume'] = df['md_domain_size'].apply(lambda l: l**3)
    if col_mamico_coupling_time_abs in df.columns:
        df['mamico_coupling_time_relative'] = df[col_mamico_coupling_time_abs] / \
            df[col_wall_time]

# Plot energy consumption
fig, axs = plt.subplots(1, 3, figsize=(16, 4))
max_full_md = df_fmd[col_energy].max()
max_energy = max(df_fmd[col_energy].max(), df_cpld[col_energy].max())

for i, (df, label) in enumerate([(df_fmd, 'Full MD'), (df_cpld, 'Coupled')]):
    x = df['md_domain_volume']
    y = df[col_energy]
    ax = axs[i]
    if i == 1:
        # 'C0--') # Only the legend label to keep it in order
        ax.plot([], 'k--', label='Full MD $\max$')
    ax.scatter(x, y, label=label, c='k')  # c=f'C{i}')
    m, c = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
    r2 = r2_score_linear(x, y, m, c)
    print(f'{label} fit: {m:.3}x+{c:.3} (r2={r2:.5})')
    label += ' fit'
    if i == 1:
        # label += f': $y={fmt_math_num(m)}x+{fmt_math_num(c)}$'
        ax.plot([x.min(), x.max()], [max_full_md,
                max_full_md], 'k--')  # 'C0--')
    ax.plot(x, m*x+c, label=label, c='k')  # c=f'C{i}')
    ax.set_ylabel('Energy consumption (kWh)')
    ax.set_ylim((0, max_energy + 0.5))
    update_axis_ticks_md_volume(ax.xaxis, df_cpld)
    # region TODO we might remove CPU time (below) from the figure
    y = df[col_cpu_time]
    if i == 0:
        ax.scatter([], [], marker='D', label=col_cpu_time.split(
            '(')[0].strip(), c='none', edgecolor='k')
    ax.legend(loc='lower right', edgecolor='k', fontsize=10, framealpha=1)
    if i == 0:
        ax = ax.twinx()
        ax.set_ylabel(col_cpu_time)
        ax.scatter(x, y, marker='D', c='none', edgecolor='k')
    # endregion (CPU time in subplot 1)

# axs[0].sharey(axs[1])
# axs[1].label_outer()
# axs[0].set_ylabel('Energy consumption (kWh)')
for ax in axs:
    ax.set_xlabel('MD domain volume')

# MaMiCo overhead


def plot_mamico_overhead_fill(df, ax):
    coupling_overhead = df_cpld.dropna()['mamico_coupling_time_relative']
    print(f'Mean coupling overhead: {coupling_overhead.mean():.5}')
    md_vol_range = (df.dropna()['md_domain_volume'].min(
    ), df.dropna()['md_domain_volume'].max())
    ax.fill_between(md_vol_range, 0, 1, edgecolor='k', label='Simulation runtime',
                    fc='lightgray')  # , hatch='.', fc='w')
    ax.fill_between(df.dropna()[
                    'md_domain_volume'], 0, coupling_overhead, edgecolor='k', label='MaMiCo coupling overhead', fc='C3')  # , hatch='//', fc='w')

    update_axis_ticks_md_volume(ax.xaxis, df)


def plot_mamico_overhead_bars(df, ax):
    df = df.dropna()
    md_vol = df['md_domain_volume']
    md_vols = list(md_vol.unique())
    md_vols.sort()
    ax.set_ylim(0, 100)

    def md_vol_to_x(md_vol):
        return md_vols.index(md_vol)
    for md_vol in md_vols:
        y = df[df['md_domain_volume'] ==
               md_vol]['mamico_coupling_time_relative']
        x = md_vol_to_x(md_vol)
        ax.bar(x, y.mean(), edgecolor='k', fc=f'C3')
    ax.fill_between([], [], edgecolor='k', fc=f'C3',
           label='MaMiCo coupling overhead')  # For legend
    # Custom error bars (NOTE: too small here to be practical)
    # ax.plot([x,x], [y.mean()-y.std(),y.mean()+y.std()], 'k')
    # for y in [y.mean()-y.std(),y.mean()+y.std()]:
    #     width = 0.25
    #     ax.plot([x-width/2,x+width/2], [y,y], 'k')
    y_mean = df['mamico_coupling_time_relative'].mean()
    ax.plot([-0.5, len(md_vols)-0.5], [y_mean, y_mean],
            'k--', label='Average MaMiCo coupling overhead')
    ax.set_xticks([md_vol_to_x(i) for i in md_vols], [f'${round(v**(1/3))}^3$' for v in md_vols])


ax = axs[-1]
df_cpld = df_cpld.sort_values(['md_domain_size', 'mamico_coupling_time'], ascending=[
                              True, True])  # Show full range of values
# plot_mamico_overhead_fill(df_cpld, ax)
plot_mamico_overhead_bars(df_cpld, ax)
ax.legend(loc='upper right', framealpha=1, edgecolor='k', fontsize=10)
ax.set_ylabel('Relative wall time')
ax.set_ylim([0, 1])
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
fig.tight_layout()

# Output visualization
if args.output is not None:
    plt.savefig(args.output)
    idx_suffix_sep = args.output.rindex('.')
    base_filename = args.output[:idx_suffix_sep]
    suffix = args.output[idx_suffix_sep:]
    x_ranges = [(0.012, 0.32), (0.338, 0.615), (0.69, 0.99)]
    for i, (x_min, x_max) in enumerate(x_ranges):
        output_file = f'{base_filename}_{i}{suffix}'
        plt.savefig(output_file, bbox_inches=mtransforms.Bbox(
            [[x_min, 0], [x_max, 1]]).transformed((fig.transFigure - fig.dpi_scale_trans)))
else:
    plt.show()
