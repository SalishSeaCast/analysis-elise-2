#!/bin/bash

#SBATCH --job-name=ncotest
#SBATCH --account=def-allen
#SBATCH --mem-per-cpu=1G
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mail-user=eolson@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --time=00:15:00
#SBATCH --output=/scratch/eolson/results/calcs/stdoutNCO2
#SBATCH --error=/scratch/eolson/results/calcs/stderrNCO2

module load python/3.7.0
module load nco/4.6.6
module load scipy-stack/2019b

echo "start python at $(date)"
python /project/def-allen/eolson/MEOPAR/analysis-elise-2/notebooks/bioTuning/bloomTiming/extraction/beluga/simpletest.py

echo "DONE at $(date)"
