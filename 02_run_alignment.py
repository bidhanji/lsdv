#!/usr/bin/env python3
"""
Script to run MAFFT alignment on LSDV genomes.

This script filters for COMPLETE genomes only (>100K bp, per the project's
own README claim), combines them into one FASTA, and then runs MAFFT to
align them.

FIXES applied vs original:
  1. Added a length filter (--min-length, default 100000) so partial /
     near-complete genomes are excluded from the alignment, matching what
     the README claims the pipeline does. The old version globbed every
     .fasta file with no length check at all.
  2. Added a hard assertion that the number of sequences going INTO MAFFT
     equals the number coming OUT. If MAFFT drops or merges a sequence
     (e.g. duplicate header, malformed entry), the script now fails loudly
     instead of printing "Alignment complete!" over silently-lost data.
  3. Skips zero-length / unparsable FASTA entries instead of blindly
     concatenating raw file content.

Author: improved for portability + correctness fixes
Date: 2026
"""

import os
import subprocess
import glob
import shutil
import argparse
import sys

parser = argparse.ArgumentParser(description="Filter, combine FASTA files and run MAFFT alignment")
parser.add_argument("--genome-dir", default="data/genomes",
                     help="Directory containing individual genome FASTA files")
parser.add_argument("--align-dir", default="data/alignment",
                     help="Directory to write combined and aligned files")
parser.add_argument("--mafft", default=None,
                     help="Path to mafft executable (or set MAFFT_PATH env var)")
parser.add_argument("--threads", default="-1",
                     help="Number of threads for MAFFT (use -1 for auto)")
parser.add_argument("--min-length", type=int, default=100000,
                     help="Minimum sequence length (bp) to include in the alignment. "
                          "Set to 0 to disable filtering.")
args = parser.parse_args()


# ---------------------------------------------------------------------
# Locate MAFFT
# ---------------------------------------------------------------------
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

genome_dir = args.genome_dir
os.makedirs(args.align_dir, exist_ok=True)

if not os.path.exists(genome_dir):
    print("ERROR: Directory", genome_dir, "does not exist!")
    print("Please run 01_download_genomes.py first or point --genome-dir to your FASTA files.")
    sys.exit(1)

fasta_files = glob.glob(os.path.join(genome_dir, "*.fasta"))
print("Found", len(fasta_files), "FASTA files in", genome_dir)

if len(fasta_files) == 0:
    print("ERROR: No FASTA files found!")
    print("Please run 01_download_genomes.py first.")
    sys.exit(1)


# ---------------------------------------------------------------------
# Parse each FASTA file, filter by length, and collect valid records.
# A minimal parser is used here (no Biopython dependency) but it handles
# multi-line sequences and skips empty / malformed entries.
# ---------------------------------------------------------------------
def parse_fasta_records(text):
    """Yield (header, sequence) tuples from raw FASTA text."""
    header = None
    seq_chunks = []
    for line in text.splitlines():
        if line.startswith(">"):
            if header is not None:
                yield header, "".join(seq_chunks)
            header = line
            seq_chunks = []
        elif line.strip():
            seq_chunks.append(line.strip())
    if header is not None:
        yield header, "".join(seq_chunks)


kept_records = []      # list of (source_file, header, sequence)
skipped_short = []     # records below min-length
skipped_empty = []     # unparsable / zero-length entries

for fasta_file in sorted(fasta_files):
    with open(fasta_file, "r") as infile:
        content = infile.read()

    file_had_record = False
    for header, seq in parse_fasta_records(content):
        file_had_record = True
        seq_len = len(seq)
        if seq_len == 0:
            skipped_empty.append((fasta_file, header))
            continue
        if seq_len < args.min_length:
            skipped_short.append((fasta_file, header, seq_len))
            continue
        kept_records.append((fasta_file, header, seq))

    if not file_had_record:
        skipped_empty.append((fasta_file, "(no header found)"))

print("\n--- Length filtering (min length = {} bp) ---".format(args.min_length))
print("Kept (complete genomes):", len(kept_records))
print("Skipped (too short / partial):", len(skipped_short))
print("Skipped (empty or unparsable):", len(skipped_empty))

if skipped_short:
    print("\nExcluded partial/near-complete genomes:")
    for fname, hdr, slen in skipped_short:
        print("  -", os.path.basename(fname), "(" + str(slen) + " bp) —", hdr[:80])

if skipped_empty:
    print("\nExcluded empty/unparsable files:")
    for fname, hdr in skipped_empty:
        print("  -", os.path.basename(fname), "—", hdr[:80])

if len(kept_records) < 2:
    print("\nERROR: Fewer than 2 sequences pass the length filter.")
    print("A meaningful alignment/tree needs at least 2 sequences.")
    print("Either lower --min-length or download more complete genomes.")
    sys.exit(1)

# ---------------------------------------------------------------------
# Write the filtered, combined FASTA
# ---------------------------------------------------------------------
combined_file = os.path.join(args.align_dir, "all_genomes_combined.fasta")
print("\nWriting filtered combined file:", combined_file)

with open(combined_file, "w") as outfile:
    for fname, header, seq in kept_records:
        outfile.write(header + "\n")
        # wrap sequence at 70 chars per line, standard FASTA convention
        for i in range(0, len(seq), 70):
            outfile.write(seq[i:i + 70] + "\n")

num_sequences_in = len(kept_records)
print("Total sequences going into MAFFT:", num_sequences_in)

# ---------------------------------------------------------------------
# Run MAFFT
# ---------------------------------------------------------------------
output_file = os.path.join(args.align_dir, "lsdv_aligned.fasta")
log_file = os.path.join(args.align_dir, "mafft.log")

mafft_command = [mafft_cmd, "--auto", "--thread", args.threads, "--reorder", combined_file]
print("\nRunning MAFFT:\n ", " ".join(mafft_command))
print("This may take some time...")

with open(output_file, "w") as out_f, open(log_file, "w") as log_f:
    proc = subprocess.run(mafft_command, stdout=out_f, stderr=log_f)

if proc.returncode != 0 or not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
    print("ERROR: MAFFT failed. See log:", log_file)
    sys.exit(proc.returncode if proc.returncode != 0 else 1)

with open(output_file, "r") as f:
    content = f.read()
aligned_count = content.count(">")

# ---------------------------------------------------------------------
# FIX #2: hard-fail if MAFFT silently dropped or merged a sequence
# ---------------------------------------------------------------------
if aligned_count != num_sequences_in:
    print("\nERROR: Sequence count mismatch after MAFFT!")
    print("  Sequences submitted to MAFFT:", num_sequences_in)
    print("  Sequences in MAFFT output:   ", aligned_count)
    print("This usually means duplicate headers were merged, or an entry")
    print("was malformed and silently dropped. Check", log_file, "and the")
    print("headers in", combined_file, "for duplicates before trusting")
    print("any downstream tree built from this alignment.")
    sys.exit(1)

# sanity check: all aligned sequences should be the same length (gaps included)
aligned_lengths = set()
current_len = 0
with open(output_file, "r") as f:
    for line in f:
        if line.startswith(">"):
            if current_len:
                aligned_lengths.add(current_len)
            current_len = 0
        else:
            current_len += len(line.strip())
    if current_len:
        aligned_lengths.add(current_len)

print("\nAlignment complete!")
print("Output file:", output_file)
print("Number of aligned sequences:", aligned_count, "(matches input count ✓)")
if len(aligned_lengths) == 1:
    print("Alignment column count (all sequences equal length):", aligned_lengths.pop())
else:
    print("WARNING: aligned sequences have inconsistent lengths:", sorted(aligned_lengths))
    print("This should not happen with a valid MAFFT alignment — investigate", log_file)

file_size = os.path.getsize(output_file)
print("File size:", file_size // 1024, "KB")

print("\nDone! Next step: build the phylogenetic tree with IQ-TREE.")
print("Run: python3 03_run_iqtree.py --alignment {} --out-dir data/tree".format(output_file))
