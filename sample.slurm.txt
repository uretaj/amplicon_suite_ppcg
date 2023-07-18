#!/bin/bash


#SBATCH --job-name=sample.slurm
#SBATCH --ntasks=4
#SBATCH -t 48:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mail-type=ALL
#SBATCH -o aa_ppcg.out
#SBATCH -e aa_ppcg.err 
#SBATCH --array=1-1
#SBATCH --mem-per-cpu=100G


module load singularity
filename="sample_name"
export MOSEKLM_LICENSE_FILE="/path/to/license"
bam="/path/to/bam"
amplicon_suite_ppcg/singularity/run_paa_singularity.py -o output/${filename} -t 4 --bam ${bam} --scna_file /path/to/scna/sample.txt --data_repo /data_repo