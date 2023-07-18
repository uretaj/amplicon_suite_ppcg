# amplicon_suite_ppcg

The original code and instructions are from https://github.com/AmpliconSuite/AmpliconSuite-pipeline . It has been modified to generate the seed intervals from the Battenberg calls, which are then passed to Amplicon Architect.

## Installation
1. Obtain the data repository containing  the AmpliconSuite-pipeline image and GRCh37 annotations  :
    * Download the data repo: /pptech_exchange/Working_Groups/ECDNA/data_repo.tar.gz.gpg
    * Extract the tar file
         ```bash
         tar zxf data_repo.tar.gz
         ```
2. Obtain the execution script
    ```bash
    git clone https://github.com/uretaj/amplicon_suite_ppcg.git
    ```
3. License for Mosek optimization tool:
    * Obtain license file `mosek.lic` (`https://www.mosek.com/products/academic-licenses/`). The license is free for academic use.
    * Place the file in `$HOME/mosek/` (i.e, the `mosek/` folder that now exists in your home directory).
    * If you are not able to place the license in the default location, you can set a custom location by exporting the bash variable   `MOSEKLM_LICENSE_FILE=/custom/path/`.
    
        ```bash
        export MOSEKLM_LICENSE_FILE="/path/to/mosek.lic"
        ```
An example command might look like:

`amplicon_suite_ppcg/singularity/run_paa_singularity.py -o path/to/output_dir/sample -t 4 --bam sample.bam  --scna_file sample.txt --data_repo path/to/data_repo `


Below is a sample Slurm file:
```bash
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
export MOSEKLM_LICENSE_FILE="/path/to/license"
bam="/path/to/bam"
amplicon_suite_ppcg/singularity/run_paa_singularity.py -o output/sample_name -t 4  --bam path/to/bam/sample_name.bam --scna_file path/to/scna/sample_name.txt --data_repo path/to/data_repo
```
## Command line arguments to AmpliconSuite-pipeline
#### Required
- `-o  {outdir}`: (Optional) Directory where results will be stored. Include the sample name to avoid conflicts.
- `-t  {int}`: (Required) Number of threads to use for BWA and CNVkit. Recommend 12 or more threads to be used.
- `--data_repo {repodir} `:  Directory where the singularity image file and  required annotations for GRCh37 are stored.

Input files:

  * `--bam | --sorted_bam {sample.bam}` Coordinate-sorted bam
  * `--scna_file {scna.txt}` Supply the Battenberg SCNA calls of the sample to generate the seed intervals to be passed to Amplicon Architect

