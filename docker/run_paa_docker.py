#!/usr/bin/env python

import argparse
import json
import os
from subprocess import call
import sys


def metadata_helper(metadata_args):
    """
    If metadata provided, this helper is used to parse it.

    input --> Metadata Args
    output --> fp to json file of sample metadata to build on
    """
    keys = "sample_metadata,sample_type,tissue_of_origin, \
            sample_description,run_metadata_file,number_of_AA_amplicons, \
            sample_source,number_of_AA_features".split(',')

    with open(metadata_args[0], 'r') as json_file:
        json_obj = json.load(json_file)

    for key_ind in range(len(keys)):
        key = keys[key_ind]
        json_obj[key] = metadata_args[key_ind]

    with open('/home/metadata.json', 'w') as json_file:
        json.dump(json_obj, json_file, indent=4)
    json_file.close()


# Parses the command line arguments
parser = argparse.ArgumentParser(
    description="A simple pipeline wrapper for AmpliconArchitect, invoking alignment, variant calling, "
    "and CNV calling prior to AA. The CNV calling is necesary for running AA")
parser.add_argument("-o", "--output_directory",
                    help="output directory names (will create if not already created)")
parser.add_argument("-s", "--sample_name", help="sample name", required=True)
parser.add_argument("-t", "--nthreads",
                    help="Number of threads to use in BWA and CNV calling", required=True)
parser.add_argument(
    "--run_AA", help="Run AA after all files prepared. Default off.", action='store_true')
parser.add_argument("--run_AC", help="Run AmpliconClassifier after all files prepared. Default off.",
                    action='store_true')
parser.add_argument("--ref", help="Reference genome version.",
                    choices=["hg19", "GRCh37", "GRCh38", "GRCh38_viral", "hg38", "mm10", "GRCm38"])
# parser.add_argument("--vcf", help="VCF (in Canvas format, i.e., \"PASS\" in filter field, AD field as 4th entry of "
# 								  "FORMAT field). When supplied with \"--sorted_bam\", pipeline will start from Canvas CNV stage."
# 					)
parser.add_argument("--cngain", type=float,
                    help="CN gain threshold to consider for AA seeding", default=4.5)
parser.add_argument("--cnsize_min", type=int, help="CN interval size (in bp) to consider for AA seeding",
                    default=50000)
parser.add_argument("--downsample", type=float,
                    help="AA downsample argument (see AA documentation)", default=10)

parser.add_argument("--AA_runmode", help="If --run_AA selected, set the --runmode argument to AA. Default mode is "
                    "'FULL'", choices=['FULL', 'BPGRAPH', 'CYCLES', 'SVVIEW'], default='FULL')
parser.add_argument("--AA_extendmode", help="If --run_AA selected, set the --extendmode argument to AA. Default "
                    "mode is 'EXPLORE'", choices=["EXPLORE", "CLUSTERED", "UNCLUSTERED", "VIRAL"], default='EXPLORE')
parser.add_argument("--AA_insert_sdevs", help="Number of standard deviations around the insert size. May need to "
                    "increase for sequencing runs with high variance after insert size selection step. (default "
                    "3.0)", type=float, default=3.0)
parser.add_argument(
    "--normal_bam", help="Path to matched normal bam for CNVKit (optional)", default=None)
parser.add_argument("--ploidy", type=int,
                    help="Ploidy estimate for CNVKit (optional)", default=None)
parser.add_argument("--purity", type=float,
                    help="Tumor purity estimate for CNVKit (optional)", default=None)
parser.add_argument("--use_CN_prefilter", help="Pre-filter CNV calls on number of copies gained above median "
                    "chromosome arm CN. Strongly recommended if input CNV calls have been scaled by purity or "
                    "ploidy. This argument is off by default but is set if --ploidy or --purity is provided for"
                    "CNVKit.", action='store_true')
parser.add_argument("--cnvkit_segmentation", help="Segmentation method for CNVKit (if used), defaults to CNVKit default"
                    " segmentation method (cbs).", choices=['cbs', 'haar', 'hmm', 'hmm-tumor', 'hmm-germline', 'none'],
                    default='cbs')
parser.add_argument("--no_filter", help="Do not run amplified_intervals.py to identify amplified seeds",
                                        action='store_true')
parser.add_argument("--align_only", help="Only perform the alignment stage (do not run CNV calling and seeding",
                    action='store_true')
parser.add_argument("--cnv_bed", help="BED file (or CNVKit .cns file) of CNV changes. Fields in the bed file should"
                    " be: chr start end name cngain", default="")
parser.add_argument("--run_as_user", help="Run the docker image as the user launching this script. Alternatively, instead of setting this flag"
                    " one can also rebuild the docker image using docker build . -t jluebeck/prepareaa:latest --build-arg set_uid=$UID --build-arg set_gid=$(id -g) ",
                    action='store_true')
parser.add_argument(
    "--no_QC", help="Skip QC on the BAM file.", action='store_true')
# parser.add_argument(
#     '--ref_path', help="Path to reference Genome. Won't download reference genome if provided.", default="None")
# parser.add_argument(
#     '--AA_seed', help='Seeds that sets randomness for AA', default=0)
parser.add_argument(
    '--metadata', help="Path to a JSON of sample metadata to build on", default="", nargs="+")


# parser.add_argument("--sample_metadata", help="Path to a JSON of sample metadata to build on")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--sorted_bam", "--bam",
                   help="Coordinate-sorted BAM file (aligned to an AA-supported reference.)")
group.add_argument("--fastqs", help="Fastq files (r1.fq r2.fq)", nargs=2)
group.add_argument("--completed_AA_runs", help="Path to a directory containing one or more completed AA runs which "
                                               "utilized the same reference genome.")

args = parser.parse_args()

if args.ref == "hg38": args.ref = "GRCh38"
if args.ref == "GRCm38": args.ref = "mm10"
if (args.fastqs or args.completed_AA_runs) and not args.ref:
    sys.stderr.write(
        "Must specify --ref when providing unaligned fastq files.")
    sys.exit(1)

if not args.output_directory:
    args.output_directory = os.getcwd()

args.output_directory = os.path.realpath(args.output_directory)
if args.output_directory == "/":
    sys.stderr.write("Output directory should not be root!\n")
    sys.exit(1)

print("making output directory read/writeable")
cmd = "chmod a+rw {} -R".format(args.output_directory)
print(cmd)
call(cmd, shell=True)

if 'AA_DATA_REPO' in os.environ:
    AA_REPO = os.environ['AA_DATA_REPO'] + "/"
    if not os.path.exists(os.path.join(AA_REPO, "coverage.stats")):
        print("coverage.stats file not found in " + AA_REPO +
              "\nCreating a new coverage.stats file.")
        cmd = "touch {}coverage.stats && chmod a+rw {}coverage.stats".format(
            AA_REPO, AA_REPO)
        print(cmd)
        call(cmd, shell=True)

else:
    AA_REPO = None
    sys.stderr.write("$AA_DATA_REPO bash variable not set. Docker image will download large (>3 Gb) data repo each"
                     " time it is run. See installation instructions to optimize this process.\n")

try:
    # MOSEK LICENSE FILE PATH
    MOSEKLM_LICENSE_FILE = os.environ['MOSEKLM_LICENSE_FILE']
    if not os.path.exists(MOSEKLM_LICENSE_FILE + "/mosek.lic"):
        raise KeyError

except KeyError:
    sys.stderr.write(
        "Mosek license (.lic) file not found. AmpliconArchitect may not be properly installed.\n")
    sys.exit(1)

# attach some directories
cnvdir, cnvname = os.path.split(args.cnv_bed)
cnvdir = os.path.realpath(cnvdir)

# assemble an argstring
argstring = "-t " + str(args.nthreads) + " --cngain " + str(args.cngain) + " --cnsize_min " + \
    str(args.cnsize_min) + " --downsample " + str(args.downsample) + " -s " + args.sample_name + \
    " -o /home/output" + " --AA_extendmode " + args.AA_extendmode + " --AA_runmode " + args.AA_runmode + \
    " --AA_insert_sdevs " + str(args.AA_insert_sdevs)

if args.ref:
    argstring += " --ref " + args.ref

if args.sorted_bam:
    args.sorted_bam = os.path.realpath(args.sorted_bam)
    bamdir, bamname = os.path.split(args.sorted_bam)
    norm_bamdir = bamdir
    argstring += " --sorted_bam /home/bam_dir/" + bamname

elif args.fastqs:
    args.fastqs[0], args.fastqs[1] = os.path.realpath(
        args.fastqs[0]), os.path.realpath(args.fastqs[1])
    _, fq1name = os.path.split(args.fastqs[0])
    bamdir, fq2name = os.path.split(args.fastqs[1])
    norm_bamdir = bamdir
    argstring += " --fastqs /home/bam_dir/" + fq1name + " /home/bam_dir/" + fq2name

else:
    argstring += " --completed_AA_runs /home/bam_dir/ --completed_run_metadata None"
    bamdir = os.path.realpath(args.completed_AA_runs)
    norm_bamdir = bamdir

if args.normal_bam:
    args.normal_bam = os.path.realpath(args.normal_bam)
    norm_bamdir, norm_bamname = os.path.split(args.normal_bam)
    argstring += " --normal_bam /home/norm_bam_dir/" + norm_bamname

if args.ploidy:
    argstring += " --ploidy " + str(args.ploidy)

if args.purity:
    argstring += " --purity " + str(args.purity)

if args.use_CN_prefilter:
    argstring += " --use_CN_prefilter"

if args.cnv_bed:
    argstring += " --cnv_bed /home/bed_dir/" + cnvname

elif args.align_only:
    argstring += " --align_only"

elif not args.completed_AA_runs:
    argstring += " --cnvkit_dir /home/programs/cnvkit.py"

if args.cnvkit_segmentation:
    argstring += " --cnvkit_segmentation " + args.cnvkit_segmentation

if args.no_filter:
    argstring += " --no_filter"

if args.no_QC:
    argstring += " --no_QC"

# To use, would need to mount the directory of this file. Users should just modify as needed afterwards.
# if args.sample_metadata:
# 	args.sample_metadata = os.path.abspath(args.sample_metadata)
# 	argstring += " --sample_metadata " + args.sample_metadata

if args.run_AA:
    argstring += " --run_AA"

if args.run_AC:
    argstring += " --run_AC"

if args.metadata != "":
    metadata_helper(args.metadata)
    argstring += " --sample_metadata /home/metadata.json"
#
# os.environ['AA_SEED'] = str(args.AA_seed)

userstring = ""
if args.run_as_user:
    userstring = " -e HOST_UID=$(id -u) -e HOST_GID=$(id -g) -u $(id -u):$(id -g)"

print("Creating a docker script with the following argstring:")
print(argstring + "\n")
with open("paa_docker.sh", 'w') as outfile:
    outfile.write("#!/bin/bash\n\n")
    outfile.write("export argstring=\"" + argstring + "\"\n")
    outfile.write("export SAMPLE_NAME=" + args.sample_name + "\n")

    # Download the reference genome if necessary
    if not AA_REPO or not (os.path.exists(AA_REPO + args.ref) and args.ref):
        outfile.write('echo DOWNLOADING {} NOW ....\n'.format(args.ref))
        outfile.write('mkdir -p /home/data_repo\n')
        outfile.write('AA_DATA_REPO=$PWD/data_repo\n')
        outfile.write(
            'wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/{}_indexed.tar.gz\n'.format(args.ref))
        outfile.write(
            'wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/{}_indexed_md5sum.txt\n'.format(args.ref))
        outfile.write(
            'tar zxf $AA_DATA_REPO/{}_indexed.tar.gz --directory $AA_DATA_REPO\n'.format(args.ref))
        outfile.write(
            'touch $AA_DATA_REPO/coverage.stats && chmod a+r $AA_DATA_REPO/coverage.stats\n')
        outfile.write('echo DOWNLOADING {} COMPLETE\n'.format(args.ref))

    # assemble a docker command string
    dockerstring = "docker run --rm" + userstring + " -e AA_DATA_REPO=/home/data_repo -e argstring=\"$argstring\"" + \
        " -v $AA_DATA_REPO:/home/data_repo -v " + bamdir + ":/home/bam_dir -v " + norm_bamdir + \
        ":/home/norm_bam_dir -v " + cnvdir + ":/home/bed_dir -v " + args.output_directory + ":/home/output -v " + \
        MOSEKLM_LICENSE_FILE + \
        ":/home/programs/mosek/8/licenses jluebeck/prepareaa bash /home/run_paa_script.sh"

    if not AA_REPO or not os.path.exists(AA_REPO + args.ref):
        outfile.write("rm -rf /home/data_repo\n")

    print("\n" + dockerstring + "\n")
    outfile.write(dockerstring)

outfile.close()

call("chmod +x ./paa_docker.sh", shell=True)
call("./paa_docker.sh", shell=True)
call("rm paa_docker.sh", shell=True)
