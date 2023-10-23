#! /usr/bin/env python3

import numpy as np
import pandas as pd

from utils import r2_score_linear

df = None

col_num_sims = 'num_md_sims'
col_snr = 'avg_snr_gain'
col_err = 'abs_vel_error'
col_md_vol = 'md_size'

for i in [60,120,180]:
    try:
        df1 = pd.read_csv(f'data/md{i}_snr_avg.csv')
        df2 = pd.read_csv(f'data/md{i}_abs_error.csv')
    except:
        print(f'Warning: File(s) for MD{i} not found!')
        continue

    df1 = df1[df1['runtype'] == 'multimd']

    # Joining did not use all values for some reason, but we know they are in order and complete
    # df1 = df1.join(df2, col_num_sims, rsuffix='__')
    df1[col_err] = df2[col_err]
    # Removing constant offset is not necessary for linear model
    # df1[col_err] -= df1[col_err].values[0]
    df1[col_md_vol] = i

    if df is None:
        df = df1
    else:
        df = pd.concat([df, df1])

df = df [[col_md_vol,col_num_sims,col_err,col_snr]]

x = df[col_err]
y = df[col_snr]

print('Correlation avg. SNR gain ~ abs. velocity error:',df[col_snr].corr(df[col_err]))
m, c = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
r2 = r2_score_linear(x, y, m, c)
print(f'SNR = {m:.3} * ERR + {c:.3} (r2={r2:.5})')

print()
