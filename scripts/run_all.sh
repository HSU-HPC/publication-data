#! /bin/bash

# This script generates MOST figures in /figures based on the data in /data

cd "$(dirname "$0")" || exit
cd ..

SCRIPTS_DIR=./scripts
DATA_DIR=./data
FIGURES_DIR=./figures

date

$SCRIPTS_DIR/get_time_stats.py > $DATA_DIR/macro_micro_timestats.csv
$SCRIPTS_DIR/plot-energy-over-md-domain-size.py $DATA_DIR/full-md-domain-size.csv -o $FIGURES_DIR/md_energy_v_size.pdf
$SCRIPTS_DIR/plot-energy-over-md-domain-size.py $DATA_DIR/prev_big_cell_runs_lc.csv -o $FIGURES_DIR/mamico_big_cell.pdf
$SCRIPTS_DIR/compare-plot-energy-over-md-domain-size.py --fmd $DATA_DIR/full-md-domain-size.csv --cpld $DATA_DIR/prev_big_cell_runs_lc.csv -o $FIGURES_DIR/energy_mamico_vs_full-md.pdf
$SCRIPTS_DIR/plot_multi-md_error.py --md60 $DATA_DIR/md60_abs_error.csv --md120 $DATA_DIR/md120_abs_error.csv --md180 $DATA_DIR/md180_abs_error.csv -o $FIGURES_DIR/multi-md_abs_error.pdf
# $SCRIPTS_DIR/plot_multi-md_energy.py --md60 $DATA_DIR/md120_snr_avg.csv  --md120 $DATA_DIR/md120_snr_avg.csv -o $FIGURES_DIR/md120_multi-md_filtering_energy.pdf
# $SCRIPTS_DIR/plot_multi-md_snr.py --md120 $DATA_DIR/md120_snr_avg.csv -o $FIGURES_DIR/md120_multi-md_filtering_snr.pdf
$SCRIPTS_DIR/error_vs_snr.py --no-show
echo "Compute correlations"
$SCRIPTS_DIR/corr_snr-abs_err.py
$SCRIPTS_DIR/plot_multi-md_v_filtering.py --md60 $DATA_DIR/md60_snr_avg.csv --md120 $DATA_DIR/md120_snr_avg.csv --md180 $DATA_DIR/md180_snr_avg.csv -c energy -o $FIGURES_DIR/multi-md_v_filtering-energy.pdf
$SCRIPTS_DIR/plot_multi-md_v_filtering.py --md60 $DATA_DIR/md60_snr_avg.csv --md120 $DATA_DIR/md120_snr_avg.csv --md180 $DATA_DIR/md180_snr_avg.csv -c snr_gain -o $FIGURES_DIR/multi-md_v_filtering-snr.pdf
$SCRIPTS_DIR/01_merge_datastets_multimd.py
$SCRIPTS_DIR/02_models.py --no-show
$SCRIPTS_DIR/time_stats_macro_micro_plot.py --no-show
$SCRIPTS_DIR/snr_gain_instance_doubling.py --no-show
# $SCRIPTS_DIR/heatmap.py --no-show # NOTE: Must update input/output filename in script manually

echo -e "\n\nDone!"
