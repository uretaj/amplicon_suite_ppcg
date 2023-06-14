# amplicon_suite_ppcg

The original code and instructions are from https://github.com/AmpliconSuite/AmpliconSuite-pipeline

## Installation
1. Obtain the AmpliconSuite-pipeline image:
   - **Singularity**:
     * Singularity installation: https://docs.sylabs.io/guides/3.0/user-guide/installation.html
     * Must have Singularity version 3.6 or higher.
     * Pull the singularity image: `singularity pull library://jluebeck/ampliconsuite-pipeline/ampliconsuite-pipeline`
2. Obtain the execution script and configure the data repo location
    ```bash
    git clone https://github.com/uretaj/AmpliconSuite-pipeline.git
    ```
3. License for Mosek optimization tool:
    * Obtain license file `mosek.lic` (`https://www.mosek.com/products/academic-licenses/`). The license is free for academic use.
    * Place the file in `$HOME/mosek/` (i.e, the `mosek/` folder that now exists in your home directory).
    * If you are not able to place the license in the default location, you can set a custom location by exporting the bash variable   `MOSEKLM_LICENSE_FILE=/custom/path/`.
     ```bash
     export MOSEKLM_LICENSE_FILE="/path/to/mosek.lic"
     ```
4. Download AA data repositories and set environment variable AA_DATA_REPO:
   -  ```bash
      cd $AA_DATA_REPO
      wget https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/GRCh37.tar.gz
      tar zxf GRCh37.tar.gz
      rm GRCh37.tar.gz
      ```
   - If you do not do this process the container runscript will attempt to download the files before launching the container.

An example command might look like:

`amplicon_suite_ppcg/singularity/run_paa_singularity.py -o /path/to/output_dir -s name_of_run -t 8 --bam bamfile.bam  --scna_file /path/to/scna_file  --ref "GRCh37" --downsample -1 --sif /path/to/singularity_image --AA_insert_sdevs 3.0  --run_AA --run_AC`

## Command line arguments to AmpliconSuite-pipeline
The complete list of arguments for AmpliconSuite is available [here](https://github.com/AmpliconSuite/AmpliconSuite-pipeline/blob/master/README.md )
#### Required
- `-o | --output_directory {outdir}`: (Optional) Directory where results will be stored. Defaults to current directory.

- `-s | --sample_name {sname}`: (Required) A name for the sample being run.

- `-t | --nthreads {int}`: (Required) Number of threads to use for BWA and CNVkit. Recommend 12 or more threads to be used.

Input files:

  * `--bam | --sorted_bam {sample.cs.bam}` Coordinate-sorted bam
  * `--scna_file {scna.txt}` Supply the SCNA calls from Battenberg
  
#### Optional

- `--run_AA`: Run AA at the end of the preparation pipeline.

- `--run_AC`: Run AmpliconClassifier following AA. No effect if `--run_AA` not set.

- `--downsample {float}`: Set a custom threshold for bam coverage downsampling during AA. Does not affect coverage in analyses outside of AA. Default: 10. Set to -1 for no downsampling.

- `--AA_insert_sdevs {float}`: Default 3.0. Suggest raising to 8 or 9 if library has poorly-controlled insert size (low fraction of properly-paired reads). See AA documentation for more info.

- `--sif {str}`: Location of the ampliconsuite-pipeline.sif file. Only required if .sif file not in cache
