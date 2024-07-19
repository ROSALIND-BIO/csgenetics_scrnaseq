# CS Genetics scRNA-Seq pipeline

**A Nextflow pipeline for processing scRNA-Seq data generated using CS Genetics' single-cell kit to produce qualtity control metrics and a gene expression matrix for single cells.**

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A521.10.3-23aa62.svg)](https://www.nextflow.io/)
[![run with docker](https://img.shields.io/badge/run%20with-docker-0db7ed?labelColor=000000&logo=docker)](https://www.docker.com/)

## Contents

- [CS Genetics scRNA-Seq pipeline](#cs-genetics-scrna-seq-pipeline)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Running the pipeline](#running-the-pipeline)
  - [Running the pipeline on MacOS](#running-the-pipeline-on-macos)
  - [Specifying input sequencing files](#specifying-input-sequencing-files)
  - [Testing the pipeline](#testing-the-pipeline)
  - [Launching the pipeline directly from the csgenetic/csgenetics\_scrnaseq Github repo](#launching-the-pipeline-directly-from-the-csgeneticcsgenetics_scrnaseq-github-repo)
    - [Updating the pipeline](#updating-the-pipeline)
    - [Specifying a pipeline version](#specifying-a-pipeline-version)
  - [Launching the pipeline from Seqera Platform](#launching-the-pipeline-from-seqera-platform)
  - [Available standard profiles](#available-standard-profiles)
    - [test](#test)
    - [test\_singularity](#test_singularity)
    - [docker](#docker)
    - [singularity](#singularity)
  - [Available curated genomic resources](#available-curated-genomic-resources)
  - [Configuring custom genomic resources](#configuring-custom-genomic-resources)
  - [Configurable parameters](#configurable-parameters)
    - [`profile`](#profile)
    - [`outdir`](#outdir)
    - [`star_index`](#star_index)
      - [Generating a STAR index](#generating-a-star-index)
    - [`gtf`](#gtf)
    - [`mitochondria_chromosome`](#mitochondria_chromosome)
    - [`barcode_list_path`](#barcode_list_path)
    - [`minimum_count_threshold`](#minimum_count_threshold)
    - [`purity`](#purity)
  - [Outputs](#outputs)
    - [`count_matrix`](#count_matrix)
    - [`report`](#report)
    - [`pipeline_info`](#pipeline_info)
    - [`fastp`](#fastp)
    - [`fastqc`](#fastqc)
    - [`featureCounts`](#featurecounts)
    - [`io_count`](#io_count)
    - [`multiqc`](#multiqc)
    - [`plots`](#plots)
    - [`qualimap`](#qualimap)
    - [`STAR`](#star)
  - [Log files](#log-files)
  - [Resource allocation](#resource-allocation)
  - [Error handling](#error-handling)
  - [Examples](#examples)
    - [Example 1](#example-1)
    - [Example 2](#example-2)

## Introduction

**CS Genetics' scRNA-Seq pipeline** is a bioinformatics best-practice analysis pipeline for processing single-cell RNA-Seq data from their single-cell RNA-Seq kits.

It runs on a Unix-like operating system (E.g. Linux).

The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a portable manner. The pipeline uses Docker to run its constituent processes making installation trivial and results reproducible.

It processes FASTQ files generated by CS Genetics' scRNA-Seq library kit to produce count matrices that can be loaded directly into [Seurat](https://satijalab.org/seurat/index.html) or [scanpy](https://scanpy.readthedocs.io/en/stable/) for further analyses.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Running the pipeline

The pipeline is run natively in your environment but uses docker containers for each of the pipeline's processes.

To run the pipeline locally, you must have Nextflow ([installation instructions](https://www.nextflow.io/docs/latest/getstarted.html#installation)) and git ([installation instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)) installed. It is recommended that you work with either the Docker or Singularity profiles
(see [Available profiles](#available-profiles) below) to enable the use of preconfigured containers for each of the pipeline processes.

For each profile, you must have the respective program installed: [Docker installation](https://docs.docker.com/get-docker/), [Singularity installation](https://docs.sylabs.io/guides/3.0/user-guide/installation.html).

With Nextflow, Docker and git installed, clone the csgenetics_scrnaseq repository to a specified directory and change into that directory.

```bash
git clone https://github.com/csgenetics/csgenetics_scrnaseq.git $HOME/analysis && cd $HOME/analysis
```

The pipeline is then run using the Nextflow executable, and in this case, the `docker` profile.

For specification of input sequences see [Specifying input sequencing files](#specifying-input-sequencing-files).

```bash
nextflow run main.nf -profile docker --input_csv $HOME/analysis/input_csv/input_csv.csv --genome GRCh38
```

For a full list of the configurable parameters that can be can be supplied to the pipeline
and other options for configuration see [Configurable parameters](#configurable-parameters).

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Running the pipeline on MacOS

While the pipeline can be launched on MacOS, some of the processes are RAM intensive.

In particular, the STAR mapping process is currently configured to run in a container that is allocated 40GB or 60GB of RAM.
The qualimap process is configured to use 16GB of RAM.

The actual resources utilized will depend on the character of the samples being analysed.

However, resource allocations will likely exceed those available on a standard MacOS laptop/desktop.

As such, it is recommened to run the pipeline on an HPC or cloud system.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Specifying input sequencing files

The sequencing files to be analysed are specified using an input csv file.

An example template can be found [here](input_csv/template.csv).

The header row must be present and the full paths to files should be given.

The `fastq_1` should contain the sequencing data that will be mapped to the genome. `fastq_2` should contain the CS Genetics barcode.

Paths may point to cloud-stored files, e.g. an AWS S3 URI, provided Nextflow supports that storage platform.
See the [Nextflow docs](https://www.nextflow.io/docs/latest/aws.html) for further details.

The full path to the input csv should be supplied to the pipeline using the `--input_csv` flag.

E.g.

```bash
nextflow run main.nf -profile docker --input_csv <path/to/csv_dir/input_csv.csv> --genome GRCh38
```

Multiple sets of sequencing files (e.g. from multiple lanes of sequencing)
can be merged by the pipeline and used for a single sample
by supplying the same sample name but with different sequencing file sets
on separate lines.

E.g.

```bash
sample,fastq_1,fastq_2
Sample1,/home/example_user/analysis/raw_reads/example_Sample1_L001_R1_001.fastq.gz,/home/example_user/analysis/raw_reads/example_Sample1_L001_R2_001.fastq.gz
Sample1,/home/example_user/analysis/raw_reads/example_Sample1_L002_R1_001.fastq.gz,/home/example_user/analysis/raw_reads/example_Sample1_L002_R2_001.fastq.gz
Sample2,/home/example_user/analysis/raw_reads/example_Sample2_L001_R1_001.fastq.gz,/home/example_user/analysis/raw_reads/example_Sample2_L001_R2_001.fastq.gz
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Testing the pipeline

To test that your environment is set up correctly, the pipeline can be run using the `test` profile:

```bash
nextflow run main.nf -profile test
```

The test proile will run using a set of remotely hosted resources. By default, the work and results directories will be created in the current working directory at `./work` and `./results`, respectively.

For a full list of the configurable parameters that can be can be supplied to the pipeline
and other options for configuration see [Configurable parameters](#configurable-parameters).

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Launching the pipeline directly from the csgenetic/csgenetics_scrnaseq Github repo

In the above examples, the csgenetics_scrnaseq git repostory was cloned locally
and the pipeline was launched specifying the main.nf Nextflow script.

Alternatively, the pipeline can be launched directly from the GitHub repository specifying its qualified name: `csgenetics/csgenetics_scrnaseq`.

See the [Nextflow documentation on Pipeline sharing](https://www.nextflow.io/docs/latest/sharing.html) for further details.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### Updating the pipeline

When launching the pipeline from a local clone of the GitHub repository, you will need to keep the pipeline up-to-date by refularly pulling down updates:

```
git pull
```

When launching the pipeline by specifying the qualified name of the pipeline, Nextflow automatically pulls the pipeline code from GitHub and stores it as a cached version. When running the pipeline after this, it will always use the cached version if available - even if the pipeline has been updated since. To make sure that you're running the latest version of the pipeline, make sure that you regularly update the cached version of the pipeline:

```bash
nextflow pull csgenetics/csgenetics_scrnaseq
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### Specifying a pipeline version

It's a good idea to specify a pipeline version (alternatively referred to as a tag or a release) when launching the pipeline. This ensures that a specific version of the pipeline code and software are used when you run your pipeline, thus ensuring reproducibilty.

See the [Nextflow documentation on Pipeline sharing](https://www.nextflow.io/docs/latest/sharing.html) for further details.

The available tags can be displayed in a cloned repository using:
`git tag`

Alternatively, the releases can be viewed [online](https://github.com/csgenetics/csgenetics_scrnaseq/releases).

For reference, the version will be logged in reports when you run the pipeline.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Launching the pipeline from Seqera Platform

The pipeline can be launched from Seqera Platform.

The repository includes a `nextflow_schema.json` file that will automatically display required parameters when launching the pipeline from your Launchpad on Seqera Platform.

To make use of containerization, don't forget to add an appropriate profile e.g. `docker` in the 'Config profiles' section of the 'Add pipeline' dialog.

## Available standard profiles

Nextflow pipeline configurable parameters can be set in groups by specifying profiles.

See the [Config profiles](https://www.nextflow.io/docs/latest/config.html#config-profiles) section of the Netflow documentation for further details.

There are five standard profiles available for the CS Genetics scRNA-Seq pipeline:

- `test`
  - A profile with a complete configuration for automated testing.
  - Includes links to test data so requires no other parameters.
  - Runs Docker containers for each process using Docker.
- `test_singularity`
  - A profile with a complete configuration for automated testing.
  - Includes links to test data so requires no other parameters.
  - Runs Docker containers for each process using Singularity.
- `docker`
  - A generic configuration profile that enables use of pre-configured Docker containers for each process run using Docker.
- `singularity`
  - A generic configuration profile that enables use of pre-configured Docker containers for each process run using Singularity.
  - See the Nextflow documentation on [Singularity](https://www.nextflow.io/docs/latest/container.html#singularity) for further details.
- `local`
  - Uses the [local executor](https://www.nextflow.io/docs/latest/executor.html#local). Software required for each process should be pre-installed on your local system.

One of the above profiles must be used for the pipeline to be configured correctly.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### test

Launching the pipeline with this profile will set configuration parameters so that remotely hosted small, human fastq files and a remotely hosted GRCh38 set of resources are used. The pipeline will use Docker containers for each of the processes.

Note that the pipeline will create the following files in your working directory:

```bash
work            # Directory containing the nextflow working files
results_test    # Finished results
.nextflow_log   # Log file from Nextflow
# Other nextflow hidden files, eg. history of pipeline runs and old logs.
```

E.g.

```bash
nextflow run main.nf -profile test
```

When running the test profile, do not supply the `--input_csv` argument. A remotely hosted input csv is used.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### test_singularity

To run the `test` profile using Singualrity to launch the Docker containers use the profile `test_singularity`

E.g.

```bash
nextflow run main.nf -profile test_singularity
```

### docker

Launching the pipeline with this profile configures the pipeline to use pre-specified Docker containers for each of the processes. It is recommended to run the pipeline using this profile.

E.g.

```bash
nextflow run main.nf -profile docker --input_csv $HOME/analysis/input_csv/input_csv.csv --genome GRCh38
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### singularity

A generic configuration profile that enables use of pre-configured Docker containers for each process run using Singularity.

E.g.

```bash
nextflow run main.nf -profile singularity --input_csv $HOME/analysis/input_csv/input_csv.csv --genome GRCh38
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Available curated genomic resources

A set of genomic resources are provided to automatically configure a pipeline run for a specific species or mix of species. To use these resources provide the relevant species key (see below) to the `--genome` command line parameter.

Resources are available for the following species:
- Human; `GRCh38` [build notes](https://s3.amazonaws.com/csgx.public.readonly/resources/references/Ensembl_Gencode_resources/STAR_2_7_11b/GRCh38.Ensembl109.GENCODEv44_with_pcLoF_without_readthrough/build_notes.txt)
- Mouse; `GRCm39` [build notes](https://s3.amazonaws.com/csgx.public.readonly/resources/references/Ensembl_Gencode_resources/STAR_2_7_11b/GRCm39.Ensembl110.GENCODEvM33_with_pcLoF_without_readthrough/build_notes.txt)
- Drosophila melanogaster; `BDGP6` [build notes](https://s3.amazonaws.com/csgx.public.readonly/resources/references/Ensembl_resources/STAR_2_7_11b/Drosophila_melanogaster.BDGP6.46/build_notes.txt)
- Pig; `Sscrofa11` [build notes](https://s3.amazonaws.com/csgx.public.readonly/resources/references/Ensembl_resources/STAR_2_7_11b/Sus_scrofa_Sscrofa11.1/build_notes.txt)
- Mixed (Human - Mouse); `mouse_human_mix` [build_notes](https://s3.amazonaws.com/csgx.public.readonly/resources/references/Ensembl_Gencode_resources/STAR_2_7_11b/GRCh38.Ensembl109.GENCODEv44_GRCm39.Ensembl110.GENCODEvM33_with_pcLoF_without_readthrough/build_notes.txt)

By passing one of these keys as an argument to `--genome`, the pipeline will automatically be configured to use the relevant set of resources for the following parameters:
- `star_index`
- `gtf`
- `mitochondria_chromosome` (`hsap_mitochondria_chromosome` & `mmus_mitochondria_chromosome` for `mouse_human_mix`)
- `hsap_gene_prefix` & `hsap_gene_prefix` (mixed species only)

E.g.

```bash
nextflow run main.nf -profile singularity --genome GRCh38 --input_csv $HOME/analysis/input_csv/input_csv.csv
```

For supplying custom genomic resources, see the [`star_index`](#star_index), [`gtf`](#gtf), and [`mitochondria_chromosome`](#mitochondria_chromosome) sections below.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Configuring custom genomic resources

To run the pipeline against a user-specified STAR index and corresponding GTF, `--genome` should be set to `custom` and the `--star_index` and `--gtf` arguments should point to the user-provided resources. The `--mitochondria_chromosome` argument should be set to the name of the mitochondrial chromosome in the genome fasta used to build the STAR index (see the [Examples](#examples), [`star_index`](#star_index), [`gtf`](#gtf), and [`mitochondria_chromosome`](#mitochondria_chromosome) sections below).

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Configurable parameters

Please refer to the [Nextflow documentation on configuration](https://www.nextflow.io/docs/latest/config.html)
for a general introduction to configuring Nextflow pipelines.

### `profile`

Use this parameter to choose a configuration profile. See [Available profiles](#available-profiles).

```bash
-profile docker
```

N.B. note the single hyphen.

### `outdir`

The output directory where the results will be saved.

```bash
--outdir <path/to/output/dir>
```

### `star_index`

Specify the path (local or cloud-based) of the STAR index directory. Required for mapping.


```bash
--star_index s3://csgx.public.readonly/resources/references/Ensembl_Gencode_resources/GRCh38.Ensembl110.GENCODEv44/star/
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

#### Generating a STAR index

If you are working with a different species or wish to create your own indexes for a different genome,
please follow the instructions for creating a STAR index [here](https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf) (section 'Generating genome indexes').

Differences in STAR build version and when running STAR for alignments can result in errors.

To avoid this, it is advised that all genomes are generated using our Docker container
that runs STAR version 2.7.11b:

```bash
docker run --rm -it -v $PWD:/mnt -w /mnt quay.io/didillysquat/samtools_star:0.0.2 \
STAR \
--runThreadN NumberOfThreads \
--runMode genomeGenerate \
--genomeDir /path/to/genomeDir \
--genomeFastaFiles /path/to/genome/fasta1 \
--sjdbGTFfile /path/to/annotations.gtf \
--sjdbOverhang ReadLength-1
```

### `gtf`

Path to the gtf (local or cloud-based) annotation file.


```bash
--gtf s3://csgx.public.readonly/resources/references/Ensembl_Gencode_resources/GRCh38.Ensembl110.GENCODEv44/genes/gencode.v44.primary_assembly.annotation.modified_seq_names.gene_subset.gtf
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### `mitochondria_chromosome`

The name of the mitochondrial chromosome in the genome fasta used to build the STAR index. DO NOT set this value if using the preconfigured set of genomic resources (see the 'genome' parameter above').


```bash
--mitochondria_chromosome 'MT'
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### `barcode_list_path`

Specify the barcode_list path to use.
The following barcode_lists are hosted remotely at:

- IDT_IO_kit_v2.csv: s3://csgx.public.readonly/resources/barcode_lists/IDT_IO_kit_v2.csv

By default the IDT_IO_kit_v2.csv barcode_list is used.

```bash
--barcode_list_path s3://csgx.public.readonly/resources/barcode_lists/IDT_IO_kit_v2.csv
```

### `minimum_count_threshold`

The minimum number of total counts for a given barcode to be considered a cell.

The cell_caller process of the module will generate a count threshold, above which, barcodes will be considered
cells. If the cell_caller determines a theshold < --minimum_count_theshold or if a theshold cannot be determined,
the --minimum_count_theshold will be used.

```bash
--minimum_count_threshold 100
```

### `purity`

A float value e.g. `0.9`. Default is `0.9`. Used only for mixed species runs as a second threshold (in addition to the minimum_count_threshold threshold) to call a single cell.

It is the number of counts from a given species divided by the total number of counts. A called cell (see minimum_count_theshold above) must have a purity greater or equal to this threshold to be considered a single cell.

```bash
--purity 0.9
```

## Outputs

The output directory is specified using the `--outdir` flag. In this directory, the pipeline outputs a number of useful results organised within the following subdirectories:

### `count_matrix`

Contains the count matrices. The matrices are output in two different formats:

- .h5ad (compatible with scanpy in Python)
- the tripartite barcodes.tsv.gz, features.tsv.gz and matrix.mtx.gz (compatible with Seurat in R)

The matrices are output as 'raw' (containing all cellular barcodes) and 'cell_only' (containing a subset of the barcodes that were classified as cells through meeting the minimum nuclear genes detected threshold).

### `report`

Contains the per sample .html reports detailing key statistics for each of the samples.
Metrics are also provided in .csv format.

Contains the experiment report that consolidates metrics for all samples.

### `pipeline_info`

Contains trace files related to the execution of the pipeline.

### `fastp`

Contains the html and json files output from the fastp QC tasks per sample.

### `fastqc`

Contains the html and .zip files output from the fastqc QC tasks per sample.

### `featureCounts`

Contains the files output from the featureCounts process including annotated and filtered bam files in addition to summary files of feature assignment.

### `io_count`

Contains the files associated with deduplication and grouping of reads.

### `multiqc`

Contains files related to the MultiQC output.

### `plots`

Plots of the Cell Caller profiles used to generate the minimum detected nuclear genes threshold
for cell calling.

The density plot describes the number of nuclear genes detected (log10 Nuclear genes) across cells. The black line describes the default cutoff value for nuclear genes when calling cells. In contrast, the red line describes the threshold determined by the cell caller.

If a red line is not present in the plot then, the default (black line) threshold has been used. If the red line is present, then the cell caller threshold has been used.

If no plots are available, this indicates there was not enough counts to produce these plots.

### `qualimap`

Contains the qualimap output logs used for assessing mapping metrics.

### `STAR`

Contains the bam files output from STAR and associated mapping log files.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Log files

As standard, Nextflow produces a `.nextflow.log` file in the directory from which the pipeline was run.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Resource allocation
### Per process

Process resource allocation uses the `withName` [process selector](https://www.nextflow.io/docs/latest/config.html#process-selectors) in the `conf/base.config` file.

To adjust the resources allocated to a process, modify this file.

Default resource allocations have been made that suit a wide variety of sample types (e.g. number of barcodes, number of reads). However, you may wish to adjust the resources allocated.

### Per pipeline launch
In addition, the total resources not to be exceeded by the pipeline when running with a local executor
can be configured in the `executor` scope in `nextflow.config`.

For example if you are running on a system that has 96GB of RAM and 32 CPUs available,
you may want to modify the `executor` scopre values from the defaults of
256 GB of RAM and 16 CPUs.

A modified scope might look like this:
```
# nextflow.config
...
executor {
  cpus = 32
  memory = '96 GB'
}
...
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Error handling

By default, when a task fails it will be retried (a maximum of 5 times) with increased RAM (`<base RAM>` * task.attempt). Both RAM and num_cpus will not be increased beyond `max_memory` (default `256.GB`) and `max_cpus` (default `16`).

`max_memory` and `max_cpus` can be set on the command line like any other parameter:

```
--max_memory 128.GB --max_cpus 8
```

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

## Examples

Below are some examples of launching the pipeline with explanations of the commands.

### Example 1

```bash
nextflow run main.nf -profile docker --input_csv <path/to/input/csv> --outdir ./results --genome custom --star_index </local/path/to/STAR_index/dir> --gtf </local/path/to/gtf> --barcode_list s3://csgx.public.readonly/resources/barcode_lists/IDT_IO_kit_v2.csv
```

A pipeline is launched using a locally installed version of
Nextflow from a locally cloned copy of the csgenetics/csgenetics_scrnaseq repository.

The user is launching against their own set of references so they have set `--genome` to `custom`,
specified a STAR index directory and a
corresponding GTF. The remotely hosted v2 barcode_list is selected explicitly.

The output directory is set to `./results`.

The docker profile is selected, configuring the pipeline to use pre-specified Docker containers for each of the processes.

The `work` directory will by created by default at `./work`.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>

### Example 2

```bash
nextflow run csgenetics/csgenetics_scrnaseq -r 0.0.34 -profile docker --input_csv <path/to/input/csv> --genome GRCh38
```

A pipeline is launched by directly specifying the GitHub repository.
Version 0.0.34 of the pipeline is used.

The `docker` profile is selected, configuring the pipeline to use pre-specified Docker containers for each of the processes.

The remotely hosted Human STAR index and GTF file are used.

The remotely hosted v2 barcode_list is used by default.

<div style="text-align: right"><a href="#cs-genetics-scrna-seq-pipeline">top</a></div>
