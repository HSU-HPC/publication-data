#! /usr/bin/env python3
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

from utils import r2_score

plt.rcParams.update({'font.size': 12})


fig = plt.figure()
ax1 = plt.gca()
ax2 = ax1.twinx()

dfs = {}
handles1 = []
handles2 = []
for i in [60, 120, 180]:
    df = pd.read_csv(f'data/md{i}_snr_avg.csv')
    df = df[df['runtype'] == 'multimd']
    df2 = pd.read_csv(f'data/md{i}_abs_error.csv')
    df['abs_vel_error'] = df2['abs_vel_error']
    dfs[i] = df

for i in dfs:
    df = dfs[i]
    handles1 += ax1.plot(df['num_md_sims'],
                         df['abs_vel_error'], '-D', label=f'MD{i} Error', alpha=0.7)
    handles2 += ax2.plot(df['num_md_sims'], df['avg_snr_gain'],
                         '--o', label=f'MD{i} SNR gain ', alpha=0.7)

# Characterize error


def c_err(x, c):
    return c/np.sqrt(x)


df = pd.concat(list(dfs.values()), ignore_index=True)
x = df['num_md_sims']
y = df['abs_vel_error']
c, _ = curve_fit(c_err, x, y)
y_hat = c_err(x, c)
r2 = r2_score(y, y_hat)
x = np.linspace(df['num_md_sims'].min(), df['num_md_sims'].max(), 100)
handles1 += ax1.plot(x, c_err(x, c), 'k-', label='Error fit')
print(f'Abs. err = {c[0]:.5}/sqrt(M) (r2={r2:.5})')

ax1.legend(handles=handles1, edgecolor='k',
           loc='upper right', bbox_to_anchor=(1, 0.45))
ax2.legend(handles=handles2, edgecolor='k',
           loc='lower right', bbox_to_anchor=(1, 0.52))
ax1.set_ylabel('Absolute Velocity Error')
ax2.set_ylabel('SNR gain (dB)')
ax1.set_xlabel('Number of MD instances')
plt.gcf().subplots_adjust(right=0.89) # Avoid cutting the right y label
plt.savefig('figures/error_v_snr.pdf')

if '--no-show' not in sys.argv:
    plt.show()

print()
