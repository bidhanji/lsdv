#!/bin/bash
# =============================================
# Script to run MAFFT alignment on LSDV genomes
# This script combines all FASTA files into one
# and then runs MAFFT to align them.
#
# Author: beginner bioinformatics student
# Date: 2026
# =============================================

# print what we are doing
echo "==========================================="
echo "STEP 2: Running MAFFT Multiple Alignment"
echo "==========================================="

# check if mafft is installed
# try system mafft first, then local install
if command -v mafft &> /dev/null; then
    MAFFT_CMD="mafft"
else
    # try local install
    LOCAL_MAFFT="/home/work/.openclaw/workspace/mafft-linux64/mafftdir/bin/mafft"
    if [ -f "$LOCAL_MAFFT" ]; then
        export MAFFT_BINARIES="/home/work/.openclaw/workspace/mafft-linux64/mafftdir/libexec"
        MAFFT_CMD="$LOCAL_MAFFT"
        echo "Using local MAFFT: $LOCAL_MAFFT"
    else
        echo "ERROR: mafft is not installed!"
        echo "Please install mafft first:"
        echo "  sudo apt install mafft"
        echo "  OR"
        echo "  conda install -c bioconda mafft"
        exit 1
    fi
fi

echo "MAFFT version:"
$MAFFT_CMD --version

# -------------------------------------------------------
# STEP 1: Combine all FASTA files into one big file
# -------------------------------------------------------
echo ""
echo "--- STEP 1: Combining all FASTA files ---"

# where our individual genomes are
GENOME_DIR="data/genomes"

# check if the genome directory exists
if [ ! -d "$GENOME_DIR" ]; then
    echo "ERROR: Directory $GENOME_DIR does not exist!"
    echo "Please run 01_download_genomes.py first."
    exit 1
fi

# count how many FASTA files we have
NUM_FILES=$(ls -1 "$GENOME_DIR"/*.fasta 2>/dev/null | wc -l)
echo "Found $NUM_FILES FASTA files in $GENOME_DIR"

if [ "$NUM_FILES" -eq 0 ]; then
    echo "ERROR: No FASTA files found in $GENOME_DIR!"
    echo "Please run 01_download_genomes.py first."
    exit 1
fi

# create output directory for alignments
mkdir -p data/alignment

# combine all FASTA files into one
COMBINED_FILE="data/alignment/all_genomes_combined.fasta"
echo "Combining all FASTA files into: $COMBINED_FILE"

# clear the output file first
> "$COMBINED_FILE"

# loop through each FASTA file and add it to the combined file
FILE_COUNT=0
for fasta_file in "$GENOME_DIR"/*.fasta
do
    FILE_COUNT=$((FILE_COUNT + 1))
    cat "$fasta_file" >> "$COMBINED_FILE"
    # make sure there is a newline between files
    echo "" >> "$COMBINED_FILE"
done

echo "Combined $FILE_COUNT files"
echo "Total sequences in combined file:"
grep -c "^>" "$COMBINED_FILE"

# -------------------------------------------------------
# STEP 2: Run MAFFT alignment
# -------------------------------------------------------
echo ""
echo "--- STEP 2: Running MAFFT alignment ---"
echo "This might take a few minutes depending on the number of sequences..."

# the input file
INPUT_FILE="$COMBINED_FILE"

# the output file
OUTPUT_FILE="data/alignment/lsdv_aligned.fasta"

# run MAFFT with these options:
# --auto : let MAFFT automatically choose the best algorithm
# --thread -1 : use all available CPU cores
# --reorder : reorder sequences by similarity (looks nicer in the tree)
echo "Running: $MAFFT_CMD --auto --thread -1 --reorder $INPUT_FILE > $OUTPUT_FILE"
echo "Please wait..."

$MAFFT_CMD --auto --thread -1 --reorder "$INPUT_FILE" > "$OUTPUT_FILE"

# check if the output file was created
if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "Alignment complete!"
    echo "Output file: $OUTPUT_FILE"
    echo "Number of aligned sequences:"
    grep -c "^>" "$OUTPUT_FILE"
    
    # show how big the file is
    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "File size: $FILE_SIZE"
    
    # show the alignment length (number of columns)
    # skip header lines (>) and count characters in the first sequence
    ALIGN_LENGTH=$(grep -v "^>" "$OUTPUT_FILE" | head -1 | wc -c)
    echo "Approximate alignment length: $ALIGN_LENGTH positions"
else
    echo "ERROR: Alignment failed! Output file not created."
    exit 1
fi

echo ""
echo "Done! Next step: build the phylogenetic tree with IQ-TREE."
echo "Run: bash 03_run_iqtree.sh"
