#! /usr/bin/env python3

from pathlib import Path
import numpy as np
import pandas as pd

root_dir = Path(__file__).parent.parent

df = None

# region Additional data/Data from additional experiments

# Experimentally verified:

md_time_steps = {
    60: 750*100,
    120: 1000*100,
    180: 100*100,
}

num_eq_timesteps = {
    60: 10_000,
    120: 5_000,
    180: 5_000,
}
# endregion

# region MultiMD merging
for md_size in [60, 120, 180]:
    infile1 = root_dir / f'data/md{md_size}_snr_avg.csv'
    infile2 = root_dir / f'data/md{md_size}_abs_error.csv'
    print(f'Reading from {infile1}')
    df1 = pd.read_csv(infile1)
    df1 = df1[df1['runtype'] == 'multimd']
    print(f'Reading from {infile2}')
    df2 = pd.read_csv(infile2)
    df1['abs_vel_error'] = df2['abs_vel_error']
    df1['md_size'] = md_size
    df1['num_eq_timesteps'] = num_eq_timesteps[md_size]
    df1['md_time_steps'] = md_time_steps[md_size]

    if df is None:
        df = df1
    else:
        df = pd.concat([df, df1], ignore_index=True)
outfile = root_dir / 'data/multimd-all.csv'
print(f'Writing all data to {outfile}')
df.to_csv(outfile)
# endregion

# region Filtering merging
df = None
vel_errs = []
for md_size in [120, 180]:
    infile1 = root_dir / f'data/md{md_size}_snr_avg.csv'
    infile2 = root_dir / f'data/md{md_size}_abs_error.csv'
    print(f'Reading from {infile1}')
    df1 = pd.read_csv(infile1)
    df1 = df1[df1['runtype'] == 'filter']
    print(f'Reading from {infile2}')
    df2 = pd.read_csv(infile2)
    vel_errs += list(df2['abs_vel_error'].values)
    df1['md_size'] = md_size
    df1['num_eq_timesteps'] = num_eq_timesteps[md_size]
    df1['md_time_steps'] = md_time_steps[md_size]

    if df is None:
        df = df1
    else:
        df = pd.concat([df, df1], ignore_index=True)
    df['abs_vel_error'] = vel_errs
outfile = root_dir / 'data/filtering-all.csv'
print(f'Writing all data to {outfile}')
df.to_csv(outfile)
# endregion
