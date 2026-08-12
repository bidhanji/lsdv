#!/usr/bin/env python3
"""
Script to run MAFFT alignment on LSDV genomes.
This script combines all FASTA files into one
and then runs MAFFT to align them.

Author: improved for portability
Date: 2026
"""

import os
import subprocess
import glob
import shutil
import argparse
import sys

parser = argparse.ArgumentParser(description="Combine FASTA files and run MAFFT alignment")
parser.add_argument("--genome-dir", default="data/genomes",
                    help="Directory containing individual genome FASTA files")
parser.add_argument("--align-dir", default="data/alignment",
                    help="Directory to write combined and aligned files")
parser.add_argument("--mafft", default=None,
                    help="Path to mafft executable (or set MAFFT_PATH env var)")
parser.add_argument("--threads", default="-1",
                    help="Number of threads for MAFFT (use -1 for auto)")
args = parser.parse_args()

# find mafft: prefer explicit argument, then env var, then PATH
def find_executable(names, env_var=None):
    if env_var:
        p = os.environ.get(env_var)
        if p and shutil.which(p):
            return p
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None

mafft_cmd = args.mafft or find_executable(["mafft"], env_var="MAFFT_PATH")
if not mafft_cmd:
    print("ERROR: MAFFT executable not found on PATH or via MAFFT_PATH.")
    print("Install MAFFT: 'sudo apt install mafft' or 'conda install -c bioconda mafft'")
    print("Or pass --mafft /full/path/to/mafft")
    sys.exit(1)

print("Using MAFFT executable:", mafft_cmd)

# where our individual genomes are
genome_dir = args.genome_dir
os.makedirs(args.align_dir, exist_ok=True)

if not os.path.exists(genome_dir):
    print("ERROR: Directory", genome_dir, "does not exist!")
    print("Please run 01_download_genomes.py first or point --genome-dir to your FASTA files.")
    sys.exit(1)

# find all FASTA files
fasta_files = glob.glob(os.path.join(genome_dir, "*.fasta"))
print("Found", len(fasta_files), "FASTA files in", genome_dir)

if len(fasta_files) == 0:
    print("ERROR: No FASTA files found!")
    print("Please run 01_download_genomes.py first.")
    sys.exit(1)

# combine all FASTA files into one
combined_file = os.path.join(args.align_dir, "all_genomes_combined.fasta")
print("Combining all FASTA files into:", combined_file)
with open(combined_file, "w") as outfile:
    for fasta_file in sorted(fasta_files):
        with open(fasta_file, "r") as infile:
            content = infile.read()
        outfile.write(content)
        outfile.write("\n")

# count how many sequences we combined
with open(combined_file, "r") as f:
    content = f.read()
num_sequences = content.count(">")
print("Combined", len(fasta_files), "files")
print("Total sequences in combined file:", num_sequences)

# run MAFFT
output_file = os.path.join(args.align_dir, "lsdv_aligned.fasta")
log_file = os.path.join(args.align_dir, "mafft.log")

mafft_command = [mafft_cmd, "--auto", "--thread", args.threads, "--reorder", combined_file]
print("Running MAFFT:\n ", " ".join(mafft_command))
print("This may take some time...")

# run and capture stderr to log
with open(output_file, "w") as out_f, open(log_file, "w") as log_f:
    proc = subprocess.run(mafft_command, stdout=out_f, stderr=log_f)

if proc.returncode != 0 or not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
    print("ERROR: MAFFT failed. See log:", log_file)
    sys.exit(proc.returncode if proc.returncode != 0 else 1)

print("\nAlignment complete!")
print("Output file:", output_file)

with open(output_file, "r") as f:
    content = f.read()
    aligned_count = content.count(">")
    print("Number of aligned sequences:", aligned_count)

file_size = os.path.getsize(output_file)
print("File size:", file_size // 1024, "KB")

print("\nDone! Next step: build the phylogenetic tree with IQ-TREE.")
print("Run: python3 03_run_iqtree.py --alignment {} --out-dir data/tree".format(output_file))
