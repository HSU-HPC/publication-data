#! /usr/bin/env python3

from pathlib import Path
import re
import subprocess
import numpy as np

base_dir = Path(__file__).parent.parent / 'raw_data'

run_folder_parent_dir_common_prefix = 'part2'

def read_output_and_print_csv(run_folder, md_size):
    path = run_folder_parent_dir_common_prefix + str(run_folder.absolute()).split(run_folder_parent_dir_common_prefix)[1]
    folder_name = run_folder.name
    # remove MultiMD 180, you should remove _4, _5, _6 (they are skewing the result too far away from the filtering)
    if any(path.endswith(f'multimd128_{i}') for i in [4,5,6]):
        return
    runtype = re.split(r'\d', folder_name)[0]
    excluded_folder_substrs = ['stacked', 'moreequ','small']
    if any(s in folder_name for s in excluded_folder_substrs) or runtype not in ['multimd', 'filter']:
        return # Not a run folder or stacked run (not representative)
    # Only consider MD sizes which are a power of 2
    num_md_sims = int(folder_name[len(runtype):].split('_')[0])
    if 0 != np.modf(np.log2(num_md_sims))[0]:
        return

    output_file = str(run_folder / 'output')
    walltime_share = subprocess.getoutput(f'cat {output_file} | grep "^Time percentages" -A1').split('\n')[1]
    walltime = ':'.join(subprocess.getoutput(f'cat {output_file} | grep "^Used walltime"').split(':')[1:]).strip()
    walltime_sec = sum([int(s) * 60**i for i,s in enumerate(walltime.split(':')[::-1])])
    print(path,runtype,num_md_sims,*[s.strip() for s in walltime_share.split(',')],walltime,walltime_sec, sep=',', end=',')
    print(md_size)

md_size_folder = {
    60: f'{run_folder_parent_dir_common_prefix}_60',
    120: f'{run_folder_parent_dir_common_prefix}',
    180: f'{run_folder_parent_dir_common_prefix}_180',
}

print('path,runtype,num_md_sims,time_percent_micro,time_percent_macro,time_percent_filter,time_percent_other,walltime_total,walltime_total_sec,md_size')
for md_size, folder in md_size_folder.items():
    for file in (base_dir / folder).iterdir():
        if not file.is_dir():
            continue
        read_output_and_print_csv(file, md_size)
