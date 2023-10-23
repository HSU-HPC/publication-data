import sys
import numpy as np
import re

def fmt_math_num(f):
    fmtd_f = f'{f:.3}'  # Format float
    # Replace 'e' with x10 and raised exponent
    fmtd_f = re.compile(r'e([+-]?[0-9]+)').sub(r'\\times10^{\1}', fmtd_f)
    fmtd_f = fmtd_f.replace('+', '')  # Remove sign for positive exponents
    fmtd_f = re.compile(r'{(-?)0+').sub(r'{\1', fmtd_f)
    return fmtd_f


def r2_score_linear(x, y, m, c):
    '''Compute prediction y_hat using mx+c and compute the R^2 score using y'''
    y_hat = np.array([m*_x+c for _x in x])
    ss_res = np.sum((y_hat - y)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1 - ss_res / ss_tot


def r2_score(y, y_hat):
    '''For predictions y_hat and corresponding observations y compute the R^2 score'''
    ss_res = np.sum((y_hat - y)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    return 1 - ss_res / ss_tot

def print_formula(form_str, params, extra_cols=[]):
    '''Colorful output (1) formula (2) formula with values substituted for parameters (3) additional text (columns)'''
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    NC='\033[0m'
    if not sys.stdout.isatty():
        # Avoid bash color escape sequences when writing to file
        (OKCYAN,OKGREEN,NC) = ['']*3
    print(f'{OKCYAN}{form_str}{NC}', end='')
    form_str_vals = form_str
    for k,v in params.items():
        if isinstance(v, int):
            form_str_vals = form_str_vals.replace(k, str(v))
        else:
            form_str_vals = form_str_vals.replace(k, f'{v:.5}')
    print(f'\t{OKGREEN}{form_str_vals}{NC}', end='')
    for c in extra_cols:
        print(f'\t{c}', end='')
    print()

def update_axis_ticks_md_volume(ax_axis, df, max_value=np.inf, step_size=1):
    # X axis ticks & label
    domain_size_range = sorted(np.unique(df['md_domain_size']))
    domain_size_range = np.array([x for x in domain_size_range if x <= max_value])
    domain_size_range = np.array([x for i,x in enumerate(domain_size_range) if i % 2 == 0])
    domain_volume = domain_size_range**3
    x_tick_labels = [f'${x}^3$' if x >= 100 else '' for x in domain_size_range]
    x_ticks = sorted(np.unique(domain_volume))
    ax_axis.set_ticks(x_ticks, x_tick_labels)
