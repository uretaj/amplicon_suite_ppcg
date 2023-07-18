# amplicon_suite_ppcg

The original code and instructions are from https://github.com/AmpliconSuite/AmpliconSuite-pipeline . It has been modified to generate the seed intervals from the Battenberg calls, which are then passed to Amplicon Architect.

## Installation
1. Obtain the data repository containing  the AmpliconSuite-pipeline image and GRCh37 annotations  :
    * Download the data repo: [url for download]
    * Extract the tar file
        ```bash
        tar zxf data_repo.tar.gz
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

`amplicon_suite_ppcg/singularity/run_paa_singularity.py -o /path/to/output_dir  -t 8 --bam bamfile.bam  --scna_file /path/to/scna_file --data_repo path/to/data_repo `

## Command line arguments to AmpliconSuite-pipeline
#### Required
- `-o | --output_directory {outdir}`: (Optional) Directory where results will be stored.

- `--data_repo {repodir} `:  Directory where the singularity image file and  required annotations for GRCh37 are stored.

- `-t | --nthreads {int}`: (Required) Number of threads to use for BWA and CNVkit. Recommend 12 or more threads to be used.

Input files:

  * `--bam | --sorted_bam {sample.bam}` Coordinate-sorted bam
  * `--scna_file {scna.txt}` Supply the SCNA calls from Battenberg to generate the seed intervals to be passed to Amplicon Architect

