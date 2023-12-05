#! /usr/bin/env python3

from pathlib import Path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import sys
plt.rcParams.update({'font.size': 12})


df_mmd = pd.read_csv(Path(__file__).parent.parent / 'data' / 'multimd-all.csv')
df_flt = pd.read_csv(Path(__file__).parent.parent / 'data' / 'filtering-all.csv')

dfs = {
    'filter' : df_flt,
    'multimd' : df_mmd,
}

for k,df in dfs.items():
    plt.figure()

    i = 0
    print(f'=== {k} ===')
    max_y = 0
    for md_size in df['md_size'].unique():
        # Just to be sure:
        df_md_size = df[df['md_size'] == md_size]
        df_md_size = df_md_size[df_md_size['runtype'] == k]
        df_md_size = df_md_size.sort_values('num_md_sims')
        num_md_sims = df_md_size['num_md_sims'].values
        num_md_sim_doublings = np.log2(num_md_sims)
        avg_snr_gaing = df_md_size['avg_snr_gain'].values
        increase = np.array([avg_snr_gaing[i] - avg_snr_gaing[i-1]
                            for i in range(1, len(num_md_sim_doublings))])
        print(f'MD{md_size} average doubling SNR gain: {increase.mean():.5} dB')
        plt.plot(num_md_sim_doublings[1:], increase,
                f'C{i}-o', label=f'MD{md_size}', alpha=0.7)
        # plt.plot(num_md_sims[1:], np.ones(len(increase)) * increase.mean(), f'C{i}--', label=f'MD{md_size} mean', alpha=0.5)
        i += 1
        max_y = max(max_y, np.max(increase))

    plt.hlines(3.010, num_md_sim_doublings[1], num_md_sim_doublings[-1], colors='k', linestyles='dashed', label='Expected value')

    plt.ylabel(f'Non-cumulative SNR gain (dB)')
    plt.xlabel(r'$n^\text{th}$ doubling of MD instances')
    plt.legend(edgecolor=f'k', framealpha=1)
    plt.ylim(0, max_y + 0.5)

    plt.savefig(Path(__file__).parent.parent /
                'figures' / f'non-cumulative-snr-gain_{k}.pdf')

    if '--no-show' not in sys.argv:
        plt.show()
