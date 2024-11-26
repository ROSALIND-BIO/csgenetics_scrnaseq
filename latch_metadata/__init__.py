
from latch.types.metadata import (
    NextflowMetadata,
    LatchAuthor,
    NextflowRuntimeResources, Params, Section, Text, ForkBranch, Fork, Spoiler
)
from latch.types.directory import LatchDir

from .parameters import generated_parameters

NextflowMetadata(
    display_name='CS Genetics SimpleCell pipeline',
    author=LatchAuthor(
        name="CS Genetics",
    ),
    parameters=generated_parameters,
    runtime_resources=NextflowRuntimeResources(
        cpus=4,
        memory=8,
        storage_gib=100,
    ),
    log_dir=LatchDir("latch:///your_log_dir"),
    flow=[
    
    #### SECTION Input/output options ####
    Section("Input/output options", Text(
"""
### Sample input
 
Sample information can be added by:
- manually adding row information,
- importing rows from Registry, or
- importing from bulk sequencing data

There should be one row for every R1/R2 pair of fastq.gz files.

For samples that use multiple fastq.gz pairs, create one row for each pair, with the same sample name.

In addition to the first three required columns:
- sample
- fastq_1
- fastq_2

an additional column(s) can be provided to manually set the cell calling theshold(s) for a given sample.

See the [Cell Caller documentation](https://github.com/csgenetics/csgenetics_scrnaseq?tab=readme-ov-file#cell-calling) for further details on cell calling.

For a single species workflow populate the manual_cellcaller_threshold.

For a mixed species workflow, populate hsap_manual_cell_caller_threshold and/or mmus_manual_cell_caller_threshold.

The cell caller thresholds should be left blank if the cell calling algorithm should be used.
"""
    ), Params('input_csv'), Params('outdir')),
    

    #### SECTION Genomic references ####
    Section("Genomic references",
        Text(
"""
### The pipeline can be run using using:
- a CS Genetics-curated reference genome, or
- a user-supplied set of genomic resources
"""),
        Fork(
            'custom_genome',
            "Choose genomic reference type",
            curated_reference = ForkBranch("Curated", Text("Select one of the curated resources below."), Params('genome')),
            custom_reference = ForkBranch("Custom", Text(
"""
### Custom genomic reference configuration

To use a custom set of genomic references you must supply the following parameters:
- The path to the STAR index directory.
- The path to the GTF file used to build the STAR index.
- The name of the mitochondria chromosome in the GTF file e.g. 'MT' or 'chrM'

**N.B. Only single species custom references are currently supported.**
"""
            ), Params('star_index'), Params('gtf'), Params('mitochondria_chromosome'))
            )
    ),
    
    #### Section cell caller theshold ####
    Spoiler("Advanced options", Text(
"""
### Minimum count threshold for cell calling
For full documentation on the minimum count threshold for cell calling (`minium_count_threshold`), please refer to the [CS Genetics' pipeline documentation](https://github.com/csgenetics/csgenetics_scrnaseq?tab=readme-ov-file#cell-calling).

For most purposes the default value of 1000 is recommended.

**N.B. If a samples cell calling threshold has been set manually, the `minimum_count_threshold` will have no effect.**
"""
    ),
    Params('minimum_count_threshold')
    )
    ]
)
