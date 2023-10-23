#! /usr/bin/env python3

import os

from matplotlib import ticker as mticker
from utils import print_formula, r2_score, update_axis_ticks_md_volume
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})


# region Constants used in our experiments
TEMPERATURE = 1.1
BOLTZ_CONST = 1
DENSITY = 0.813
CELL_VOL = 5**3
TIMESTEPS_FULL_MD_EXPERIMENT = 100_000

# Alternative constants from ls1 mardyn
NUM_PARTICLES_MD60 = 171500
NUM_MACRO_CELL_SIZE = 5**3
DOMAIN_VOLUME_MD60 = 60**3
NUM_CELLS_MD60 = DOMAIN_VOLUME_MD60 / NUM_MACRO_CELL_SIZE
# endregion

FULL_MD_EXPERIMENT_TIMESTEPS = 100000  # For data/full-md-domain-size.csv

# region Energy model 1 full-MD instance
df_fullmd = pd.read_csv(Path(__file__).parent.parent /
                        'data/full-md-domain-size.csv')
x = df_fullmd['md_domain_size'] ** 3
y = df_fullmd['energy_consumption_kWh']
energy_eq_beta_1, energy_eq_beta_2 = np.linalg.lstsq(
    np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]


def energy_md(V): return energy_eq_beta_1*V+energy_eq_beta_2


r2 = r2_score(y, energy_md(x))
formula = f'energy_md(v) = beta_1 * v + beta_2'
print_formula(formula, {'beta_2': energy_eq_beta_2,
              'beta_1': energy_eq_beta_1}, [f'r2={r2:.5}'])
# endregion

df_mmd = pd.read_csv(Path(__file__).parent.parent / 'data/multimd-all.csv')
df_fil = pd.read_csv(Path(__file__).parent.parent / 'data/filtering-all.csv')

print('----------')
for runtype, df_runtype in [('multi-MD', df_mmd), ('filtering', df_fil)]:
    print(runtype.upper()+':')
    # region SNR gain model from M instances
    x = np.log(df_runtype['num_md_sims'])
    y = df_runtype['avg_snr_gain']
    snr_gamma_1, snr_gamma_2 = np.linalg.lstsq(
        np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]

    def snr_from_logM(logM): return snr_gamma_1*logM+snr_gamma_2

    r2 = r2_score(y, snr_from_logM(x))
    formula = f'mean SNR(M) = gamma_1 * log M + gamma_2'
    print_formula(formula, {'gamma_2': snr_gamma_2,
                  'gamma_1': snr_gamma_1}, [f'r2={r2:.5}'])
    # endregion

    # region SNR gain model from error
    def snr(e):
        return snr_gamma_1*np.log((TEMPERATURE*BOLTZ_CONST*NUM_CELLS_MD60) / (NUM_PARTICLES_MD60*e**2))+snr_gamma_2
        # return snr_beta1*np.log((TEMPERATURE*BOLTZ_CONST) / (DENSITY*CELL_VOL*e**2))+snr_beta0

    x = df_runtype['abs_vel_error']
    r2 = r2_score(y, snr(x))
    formula = f'mean SNR(e) = gamma_1*log((temp*k*num_cells) / (num_particles*e**2))+gamma_2'
    print_formula(formula, {'num_cells': NUM_CELLS_MD60, 'num_particles': NUM_PARTICLES_MD60, 'temp': TEMPERATURE, 'k': BOLTZ_CONST, 'density': DENSITY,
                  'volume_cell': CELL_VOL, 'gamma_2': snr_gamma_2, 'gamma_1': snr_gamma_1}, [f'r2={r2:.5}'])
    # endregion
    print('----------')
# region Energy model M full-MD instances


def get_energy_no_eq(i):
    r = df_mmd.iloc[i]
    return r['avg_energy'] - energy_md(r['md_size']**3)/TIMESTEPS_FULL_MD_EXPERIMENT*r['num_eq_timesteps']


df_mmd['avg_energy_no_eq'] = [get_energy_no_eq(i) for i in range(len(df_mmd))]
df_mmd['avg_energy_per_timestep'] = df_mmd['avg_energy_no_eq'] / \
    df_mmd['md_time_steps']

df_mmd['md_volume'] = df_mmd['md_size']**3


energy_formula = '(alpha_1 * V + alpha_2)*(beta_1 * M + beta_2)'


def energy_coupled(X, alpha_1, alpha_2, beta_1, beta_2):
    # X is a vector containing the MD volume and number of MD instances
    V = X[0]
    M = X[1]
    return eval(energy_formula)


def filter_out_outliers(df):
    # NOTE Filter out known outliers (around >120 nodes and >=160^3 MD volume causes some hardware overhead, likely communication)
    mask = df['num_md_sims'] <= 120
    mask |= df['md_size'] < 160
    if 'is_stacked_run' in df.columns:
        mask |= df['is_stacked_run']
    return pd.DataFrame(df[mask])


df_mmd_fit = filter_out_outliers(df_mmd)
X = df_mmd_fit[['md_volume', 'num_md_sims']].values.T
y = df_mmd_fit['avg_energy_per_timestep'].values
fitted_params, _ = curve_fit(energy_coupled, X, y, method='dogbox')

df_mmd_fit.dropna(inplace=True)


(alpha_1, alpha_2, beta_1, beta_2) = fitted_params
r2 = r2_score(y, energy_coupled(X, *fitted_params))
formula = f'energy_coupled(V,M) = {energy_formula}'
print_formula(formula, {'alpha_1': alpha_1, 'alpha_2': alpha_2,
              'beta_1': beta_1, 'beta_2': beta_2}, [f'r2={r2:.5}'])

# Visualize final energy model
KWH_TO_WH = 1_000


def compute_energy_per_timestep(r):
    eq_energy = (r['eq_timesteps'] / FULL_MD_EXPERIMENT_TIMESTEPS) * \
        energy_md(r['md_volume'])
    return (r['total_energy'] - eq_energy) / r['timesteps']


df_test_data = pd.read_csv('data/test_data_fitted_model.csv')
df_test_data.drop(['snr_gain'], axis=1, inplace=True)
df_test_data.dropna(inplace=True)
# Drop all runs using only 1 node
df_test_data = df_test_data[df_test_data['num_md_sims'] != 1]
df_test_data['md_volume'] = df_test_data['md_size'].values ** 3
df_test_data['avg_energy_per_timestep'] = df_test_data.apply(
    compute_energy_per_timestep, axis=1)

fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(projection='3d')

# Polygon (what we interpolate)
cols_plot = ['md_volume', 'num_md_sims', 'avg_energy_per_timestep']
data = {}
for c in cols_plot:
    data[c] = np.append(df_mmd[c].values, df_test_data[c].values)
    print(c, data[c].shape)
df_surface = pd.DataFrame(data)
x = df_surface['md_volume'].unique()
y = df_surface['num_md_sims'].unique()
x, y = np.meshgrid(x, y)

# Polygon (our model)
z_hat = energy_coupled([x, y], *fitted_params)
z_hat = np.reshape(z_hat, x.shape) * KWH_TO_WH
# FIXME Do not plot surface because it looks quite messy
# ax.plot_surface(x, y, z_hat, alpha=0.3, facecolor='k', shade=True)
# Overlay grid for better visibility
grid_size = 20
grid_alpha = 0.3
x_range = np.linspace(df_surface['md_volume'].min(),
                      df_surface['md_volume'].max(), grid_size)
y_range = np.linspace(df_surface['num_md_sims'].min(),
                      df_surface['num_md_sims'].max(), grid_size)
for i in range(grid_size):
    _x = [x_range[i]]*len(y_range)
    z_hat_range = energy_coupled(
        np.array([_x, y_range]), *fitted_params) * KWH_TO_WH
    ax.plot(_x, y_range, z_hat_range, 'k-', alpha=grid_alpha)
    _y = [y_range[i]]*len(x_range)
    z_hat_range = energy_coupled(
        np.array([x_range, _y]), *fitted_params) * KWH_TO_WH
    ax.plot(x_range, _y, z_hat_range, 'k-', alpha=grid_alpha)
# Hide 3d plot grid because it would otherwhise be hard to read
for a in ['x', 'y', 'z']:
    exec(f'ax.{a}axis._axinfo["grid"]["color"] = (1,1,1,0)')
    exec(f'ax.{a}axis.set_pane_color((1.0, 1.0, 1.0, 0.0))')


def plot_observation_difference(x, y, z, color='r', alpha=1.0):
    z_hat = energy_coupled([x, y], *fitted_params)
    # plt.plot(x, y, z_hat, 'k.', zorder=10)
    z_err = z - z_hat
    xyz_e_pos = ([], [], [])
    xyz_e_neg = ([], [], [])
    for p in zip(x, y, z_hat, z_err):
        (_x, _y, _z, e) = p
        plt.plot([_x, _x], [_y, _y], [_z * KWH_TO_WH, (_z+e)
                 * KWH_TO_WH], f'{color}-', alpha=alpha)
        xyz_e = xyz_e_pos if e >= 0 else xyz_e_neg
        xyz_e[0].append(_x)
        xyz_e[1].append(_y)
        xyz_e[2].append((_z+e) * KWH_TO_WH)
    plt.plot(*xyz_e_pos, f'{color}^', zorder=10, alpha=alpha)
    plt.plot(*xyz_e_neg, f'{color}v', zorder=10, alpha=alpha)
    return z_hat, z_err.values


# Line plot (what we observe + our model)
y = df_mmd_fit['num_md_sims']
x = df_mmd_fit['md_volume']
z = df_mmd_fit['avg_energy_per_timestep']
plot_observation_difference(x, y, z, color='b')

alpha_outlier = 0.3


def plot_outliers(df_all, df_filtered):
    df_outliers = df_all.drop(df_filtered.index)
    y = df_outliers['num_md_sims']
    x = df_outliers['md_volume']
    z = df_outliers['avg_energy_per_timestep']
    plot_observation_difference(x, y, z, color='r', alpha=alpha_outlier)


plot_outliers(df_mmd, df_mmd_fit)

# Now also for the test data
# num_md_sims,md_domain_size,total_energy,timesteps,eq_timesteps

df_test_data_no_outliers = filter_out_outliers(df_test_data)
V = df_test_data_no_outliers['md_volume']
M = df_test_data_no_outliers['num_md_sims']
z = df_test_data_no_outliers['avg_energy_per_timestep']
z_hat, z_err = plot_observation_difference(V, M, z, color='r')
plot_outliers(df_test_data, df_test_data_no_outliers)
z_err = np.abs(z_err)  # Remove sign
z_err_percent = z_err / z * 100
print(
    f'\ntest data error (kWh): mean={np.mean(z_err):.5}, stdev={np.std(z_err):.5}, max={np.max(z_err):.5}')
print(
    f'test data error (%): mean={np.mean(z_err_percent):.5}%, stdev={np.std(z_err_percent):.5}%, max={np.max(z_err_percent):.5}%\n')

df_test_data_no_outliers['model_timestep_energy'] = z_hat
df_test_data_no_outliers['model_error'] = z_err
df_test_data_no_outliers['model_error_percent'] = z_err_percent
df_test_data_no_outliers.sort_values('model_error_percent', inplace=True)

# region Output table with test data for paper
print('LaTeX table of test data results:')
df_test_data_latex = df_test_data_no_outliers.copy()
df_test_data_latex['num_nodes'] = df_test_data_latex.apply(lambda r: int(r['num_md_sims'] / (2 if r['is_stacked_run'] else 1)), axis=1)
df_test_data_latex = df_test_data_latex[['md_size','num_md_sims','num_nodes','model_error','model_error_percent']]
df_test_data_latex['model_error'] *= KWH_TO_WH
df_test_data_latex['model_error_percent'] /= 100 # Convert to fraction (Formatter converts back to percent)
df_test_data_latex.sort_values(['md_size','num_md_sims'], inplace=True)
columns = ['MD domain volume', 'Number of MD instances', 'Number of nodes', 'Absolute model error', 'Relative model error']
df_test_data_latex.columns = columns
print(df_test_data_latex.to_latex(formatters={
    columns[0]: '${:d}^3$'.format,
    # 1 default
    # 2 default
    columns[3]: '${:.5f}\\,\\text{{Wh}}$'.format,
    columns[4]: '${:.5%}$'.format,
}, index=False).replace('%', r'\%'))
# endregion

df_test_stacked = df_test_data_no_outliers[df_test_data_no_outliers['is_stacked_run']]
V = df_test_stacked['md_volume']
M = df_test_stacked['num_md_sims']
z = df_test_stacked['avg_energy_per_timestep']
plot_observation_difference(V, M, z, color='g')

plt.plot([], [], 'b-', label='Difference to fitting observation')
plt.plot([], [], 'r-', label='Difference to test observation')
plt.plot([], [], 'r-', alpha=alpha_outlier, label='Removed outlier')
plt.plot([], [], 'g-', label='Stacked run (2 MD instances per node)')
ax.legend(loc='upper left', framealpha=1, edgecolor='k',
          fontsize=12, bbox_to_anchor=(0.15, 0.7))
plt.ylabel('Number of MD instances')
ax = plt.gca()
update_axis_ticks_md_volume(
    ax.xaxis, df_fullmd, max_value=1+df_mmd['md_volume'].max()**(1/3), step_size=2)
ax.yaxis.set_major_locator(mticker.FixedLocator(ax.get_yticks().tolist()))
ax.set_yticklabels(ax.get_yticklabels(),
                   verticalalignment='baseline', horizontalalignment='left')
plt.xlabel('MD domain volume')
for a in ['x', 'y', 'z']:
    exec(f'ax.{a}axis.labelpad = 20')
ax.set_zlabel('Avg. energy consumption per time step (Wh)')
# plt.tight_layout()
ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

output_file = 'figures/energy_model.pdf'
plt.savefig(output_file)
os.system(f'pdfcrop {output_file} {output_file}')

if '--no-show' not in sys.argv:
    plt.show()
# endregion

print()
