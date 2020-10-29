#!/bin/bash

#SBATCH --job-name=ncotest
#SBATCH --account=def-allen
#SBATCH --mem-per-cpu=4G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --mail-user=eolson@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --time=12:00:00
#SBATCH --output=/scratch/eolson/results/calcs/stdoutNCO
#SBATCH --error=/scratch/eolson/results/calcs/stderrNCO

module load python/3.7.0
module load nco/4.6.6
module load scipy-stack/2019b

echo "start python at $(date)"
python /project/def-allen/eolson/MEOPAR/analysis-elise-2/notebooks/bioTuning/bloomTiming/extraction/beluga/testbeluga.py

echo "DONE at $(date)"
