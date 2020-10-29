#!/bin/bash

#SBATCH --job-name=ncotest
#SBATCH --account=def-allen
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks=11
#SBATCH --mail-user=eolson@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --time=12:00:00
#SBATCH --output=/scratch/eolson/results/calcs/stdoutNCO
#SBATCH --error=/scratch/eolson/results/calcs/stderrNCO

module load python/3.7.0
module load nco/4.6.6
module load scipy-stack/2019b

echo "virtualenv at $(date)"

virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip
pip install angles
pip install arrow
pip install bottleneck
pip install cmocean
pip install f90nml
pip install gsw
pip install matplotlib
pip install netCDF4
pip install progressbar
pip install python-dateutil
pip install pytz
pip install requests
pip install retrying
pip install scipy
pip install xarray
pip install /project/def-allen/eolson/MEOPAR/tools/SalishSeaTools

echo "start python at $(date)"
python /project/def-allen/eolson/MEOPAR/analysis-elise-2/notebooks/bioTuning/bloomTiming/extraction/beluga/testbeluga.py tvdTune_201812ESSMORT

echo "DONE at $(date)"
