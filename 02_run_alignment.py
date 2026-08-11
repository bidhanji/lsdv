#!/usr/bin/env python3
"""
Script to run MAFFT alignment on LSDV genomes.
This script combines all FASTA files into one
and then runs MAFFT to align them.

Author: beginner bioinformatics student
Date: 2026
"""

# import what we need
import os
import subprocess
import glob

# print what we are doing
print("===========================================")
print("STEP 2: Running MAFFT Multiple Alignment")
print("===========================================")

# -------------------------------------------------------
# STEP 1: Find MAFFT executable
# -------------------------------------------------------
print("\n--- Looking for MAFFT ---")

# try system mafft first
mafft_cmd = "mafft"

# check if mafft is installed system-wide
try:
    result = subprocess.run([mafft_cmd, "--version"], capture_output=True, text=True)
    print("Found system MAFFT:", result.stdout.strip())
except FileNotFoundError:
    # try local install
    local_mafft = "/home/work/.openclaw/workspace/mafft-linux64/mafftdir/bin/mafft"
    if os.path.exists(local_mafft):
        mafft_cmd = local_mafft
        os.environ["MAFFT_BINARIES"] = "/home/work/.openclaw/workspace/mafft-linux64/mafftdir/libexec"
        print("Using local MAFFT:", local_mafft)
    else:
        print("ERROR: MAFFT not found!")
        print("Please install MAFFT:")
        print("  sudo apt install mafft")
        print("  OR conda install -c bioconda mafft")
        exit(1)

# -------------------------------------------------------
# STEP 2: Combine all FASTA files into one
# -------------------------------------------------------
print("\n--- STEP 1: Combining all FASTA files ---")

# where our individual genomes are
genome_dir = "data/genomes"

# check if directory exists
if not os.path.exists(genome_dir):
    print("ERROR: Directory", genome_dir, "does not exist!")
    print("Please run 01_download_genomes.py first.")
    exit(1)

# find all FASTA files
fasta_files = glob.glob(os.path.join(genome_dir, "*.fasta"))
print("Found", len(fasta_files), "FASTA files in", genome_dir)

if len(fasta_files) == 0:
    print("ERROR: No FASTA files found!")
    print("Please run 01_download_genomes.py first.")
    exit(1)

# create output directory
os.makedirs("data/alignment", exist_ok=True)

# combine all FASTA files into one
combined_file = "data/alignment/all_genomes_combined.fasta"
print("Combining all FASTA files into:", combined_file)

# open the output file for writing
with open(combined_file, "w") as outfile:
    # loop through each FASTA file
    for fasta_file in sorted(fasta_files):
        # read the file
        with open(fasta_file, "r") as infile:
            content = infile.read()
        # write to combined file
        outfile.write(content)
        # make sure there is a newline between files
        outfile.write("\n")

# count how many sequences we combined
with open(combined_file, "r") as f:
    content = f.read()
    num_sequences = content.count(">")
    print("Combined", len(fasta_files), "files")
    print("Total sequences in combined file:", num_sequences)

# -------------------------------------------------------
# STEP 3: Run MAFFT alignment
# -------------------------------------------------------
print("\n--- STEP 2: Running MAFFT alignment ---")
print("This might take a few minutes...")

# the input and output files
input_file = combined_file
output_file = "data/alignment/lsdv_aligned.fasta"

# build the MAFFT command
# --auto : let MAFFT choose the best algorithm
# --thread -1 : use all CPU cores
# --reorder : reorder sequences by similarity
mafft_command = [mafft_cmd, "--auto", "--thread", "-1", "--reorder", input_file]

print("Running:", " ".join(mafft_command))
print("Please wait...")

# run MAFFT
# subprocess.run runs a command and waits for it to finish
# stdout goes to the output file
# stderr goes to a log file
with open(output_file, "w") as out_f:
    with open("data/alignment/mafft.log", "w") as log_f:
        result = subprocess.run(mafft_command, stdout=out_f, stderr=log_f)

# check if it worked
if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
    print("\nAlignment complete!")
    print("Output file:", output_file)

    # count aligned sequences
    with open(output_file, "r") as f:
        content = f.read()
        aligned_count = content.count(">")
        print("Number of aligned sequences:", aligned_count)

    # file size
    file_size = os.path.getsize(output_file)
    print("File size:", file_size // 1024, "KB")
else:
    print("ERROR: Alignment failed!")
    print("Check the log: data/alignment/mafft.log")
    exit(1)

print("\nDone! Next step: build the phylogenetic tree with IQ-TREE.")
print("Run: python3 03_run_iqtree.py")
