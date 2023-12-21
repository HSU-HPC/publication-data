#! /usr/bin/env python3

import os
from pathlib import Path
import subprocess
import sys

os.chdir(Path(__file__).parent)

BASE_DIR = '../raw_data'
OUTPUT_FILE_SUFFIXES = [
    '.log',
    'output'
]

# cmd = "find ../raw_data/ | grep -E '(\.log)|(output)$'"
cmd = f"find {BASE_DIR} | grep -E '" + \
    '|'.join('(' + s.replace('.', '\\.')+')' for s in OUTPUT_FILE_SUFFIXES) + "$'"

ps = subprocess.Popen(
    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output_files = ps.communicate()[0].decode('utf-8').strip().splitlines()

total_walltime_sec = 0
total_cputime_sec = 0


def parse_time_from_output_line(line):
    time_fmtd = line.split(' : ')[1].split('(')[0].strip()
    time_in_seconds = 0
    if '-' in time_fmtd:
        days, time_fmtd = time_fmtd.split('-')
        time_in_seconds += int(days) * 24 * 3600
    seconds_per_unit = 1
    for units in time_fmtd.split(':')[::-1]:
        time_in_seconds += int(units) * seconds_per_unit
        seconds_per_unit *= 60
    return time_in_seconds


def fmt_time(s):
    m = int(s / 60)
    s -= m * 60
    h = int(m / 60)
    m -= h * 60
    d = int(h / 24)
    h -= d * 24
    return f'{d}-{h:02d}:{m:02d}:{s:02d} or roughly {d*24+h+(1 if m >= 30 else 0)} hours'


for file in output_files:
    print(f'Processing {file}...', file=sys.stderr)
    for line in Path(file).read_text().splitlines():
        if line.startswith('Used walltime'):
            total_walltime_sec += parse_time_from_output_line(line)
        elif line.startswith('Used CPU time'):
            total_cputime_sec += parse_time_from_output_line(line)

print(file=sys.stderr)
print('Total wall time:', f'{total_walltime_sec} sec',
      f'({fmt_time(total_walltime_sec)})')
print('Total CPU time:', f'{total_cputime_sec} sec',
      f'({fmt_time(total_cputime_sec)})')
