#!/usr/bin/env python3
"""
Script to build a phylogenetic tree with IQ-TREE.
This takes the aligned sequences and builds
a maximum likelihood tree.

Author: beginner bioinformatics student
Date: 2026
"""

# import what we need
import os
import subprocess

# print what we are doing
print("===========================================")
print("STEP 3: Building Phylogenetic Tree")
print("===========================================")

# -------------------------------------------------------
# STEP 1: Find IQ-TREE executable
# -------------------------------------------------------
print("\n--- Looking for IQ-TREE ---")

# try system iqtree first
iqtree_cmd = "iqtree2"

try:
    result = subprocess.run([iqtree_cmd, "--version"], capture_output=True, text=True)
    print("Found system IQ-TREE:", result.stdout.strip()[:50])
except FileNotFoundError:
    # try local install
    local_iqtree = "/home/work/.openclaw/workspace/iqtree-2.3.6-Linux-intel/bin/iqtree2"
    if os.path.exists(local_iqtree):
        iqtree_cmd = local_iqtree
        print("Using local IQ-TREE:", local_iqtree)
    else:
        print("ERROR: IQ-TREE not found!")
        print("Please install IQ-TREE:")
        print("  sudo apt install iqtree")
        print("  OR conda install -c bioconda iqtree")
        exit(1)

# -------------------------------------------------------
# STEP 2: Check if alignment file exists
# -------------------------------------------------------
print("\n--- STEP 1: Checking input file ---")

alignment_file = "data/alignment/lsdv_aligned.fasta"

if not os.path.exists(alignment_file):
    print("ERROR: Alignment file not found:", alignment_file)
    print("Please run 02_run_alignment.py first.")
    exit(1)

print("Alignment file found:", alignment_file)

# count sequences
with open(alignment_file, "r") as f:
    content = f.read()
    num_sequences = content.count(">")
    print("Number of sequences:", num_sequences)

# -------------------------------------------------------
# STEP 3: Run IQ-TREE
# -------------------------------------------------------
print("\n--- STEP 2: Running IQ-TREE ---")
print("This will take some time. IQ-TREE tests different models.")
print("")

# create output directory
os.makedirs("data/tree", exist_ok=True)

# build the IQ-TREE command
# -s : input alignment file
# -m MFP : Model Finder Plus (tests many models, picks best)
# -bb 1000 : ultrafast bootstrap with 1000 replicates
# -nt AUTO : automatically choose number of threads
# -pre : prefix for output files
iqtree_command = [
    iqtree_cmd,
    "-s", alignment_file,
    "-m", "MFP",
    "-bb", "1000",
    "-nt", "AUTO",
    "-pre", "data/tree/lsdv_tree",
    "-redo"
]

print("Running:", " ".join(iqtree_command))
print("")

# run IQ-TREE
result = subprocess.run(iqtree_command, capture_output=False)

# -------------------------------------------------------
# STEP 4: Check results
# -------------------------------------------------------
print("\n--- STEP 3: Checking results ---")

tree_file = "data/tree/lsdv_tree.treefile"

if os.path.exists(tree_file):
    print("Tree file created successfully!")
    print("Tree file:", tree_file)
    print("")

    # show first part of tree
    with open(tree_file, "r") as f:
        tree_content = f.read()
    print("Tree (first 200 chars):")
    print(tree_content[:200])
    print("")

    # show all output files
    print("All IQ-TREE output files:")
    for f in sorted(os.listdir("data/tree")):
        if f.startswith("lsdv_tree"):
            filepath = os.path.join("data/tree", f)
            size = os.path.getsize(filepath)
            print("  -", f, "(" + str(size) + " bytes)")

    # try to find the best model from log
    log_file = "data/tree/lsdv_tree.log"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                if "Best-fit model" in line:
                    print("\n" + line.strip())
                    break
else:
    print("ERROR: Tree file was not created!")
    print("Check the log: data/tree/lsdv_tree.log")
    exit(1)

print("\nDone! Next step: visualize the tree.")
print("Run: python3 04_visualize_tree.py")
