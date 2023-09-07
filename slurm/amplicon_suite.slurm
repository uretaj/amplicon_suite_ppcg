#!/bin/bash


#SBATCH --job-name=circdna.slurm
#SBATCH --ntasks=1
#SBATCH -t 48:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mail-type=ALL
#SBATCH --output=%x.%a.%j.out # STDOUT 
#SBATCH --error=%x.%a.%j.err  # STDERR
#SBATCH --array=1-40
#SBATCH --mem-per-cpu=100G



module load singularity/3.8.2
export MOSEKLM_LICENSE_FILE="mosek/mosek.lic"
echo "ARRAY ID: ${SLURM_ARRAY_TASK_ID}"
filename=$(head -n ${SLURM_ARRAY_TASK_ID} hlfa_list_all_countries.csv  | tail -1)
filename=${filename%$'\r'}
IFS=',' read -ra arr <<< "$filename"
sample=${arr[0]}
cnv=${arr[1]}
echo "SAMPLE ${sample}"
echo "FILENAME ${cnv}"
pathf="BAM/${sample}.mapped.bam"
cnvpath="Subclonal_SCNA_with_Avg_CN/${cnv}
amplicon_suite_ppcg/singularity/run_paa_singularity.py  -o AA_RESULT/${sample}  --bam ${pathf}  --scna_file ${cnvpath} --data_repo /home/data_repo
