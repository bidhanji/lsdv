#!/usr/bin/env python3
"""
Script to build a phylogenetic tree with IQ-TREE.

Takes the aligned sequences and builds a maximum likelihood tree.
- Looks for iqtree2 or iqtree on PATH
- Accepts --iqtree or IQTREE_PATH env var to point to a custom binary

Author: improved for portability
Date: 2026
"""
import os
import subprocess
import argparse
import shutil
import sys

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

parser = argparse.ArgumentParser(description="Run IQ-TREE on an alignment")
parser.add_argument("--alignment", "-a", default="data/alignment/lsdv_aligned.fasta",
                    help="Input alignment FASTA file")
parser.add_argument("--out-dir", "-o", default="data/tree",
                    help="Output directory for IQ-TREE files")
parser.add_argument("--iqtree", default=None,
                    help="Path to iqtree executable (or set IQTREE_PATH env var)")
parser.add_argument("--threads", default="AUTO",
                    help="Number of threads for IQ-TREE (e.g. AUTO or N)")
parser.add_argument("--bb", default="1000",
                    help="Ultrafast bootstrap replicates (e.g. 1000)")

args = parser.parse_args()

iqtree_cmd = args.iqtree or find_executable(["iqtree2", "iqtree"], env_var="IQTREE_PATH")
if not iqtree_cmd:
    print("ERROR: IQ-TREE (iqtree2/iqtree) not found on PATH or via IQTREE_PATH.")
    print("Install IQ-TREE: 'sudo apt install iqtree' or 'conda install -c bioconda iqtree'")
    print("Or pass --iqtree /full/path/to/iqtree")
    sys.exit(1)

print("Using IQ-TREE executable:", iqtree_cmd)

if not os.path.exists(args.alignment):
    print(f"ERROR: Alignment file not found: {args.alignment}")
    print("Make sure you've run the alignment step (02_run_alignment.py) and provided the correct --alignment path.")
    sys.exit(1)

os.makedirs(args.out_dir, exist_ok=True)

prefix = os.path.join(args.out_dir, "lsdv_tree")

iqtree_command = [
    iqtree_cmd,
    "-s", args.alignment,
    "-m", "MFP",
    "-bb", args.bb,
    "-nt", args.threads,
    "-pre", prefix,
    "-redo"
]

print("Running IQ-TREE:")
print(" ", " ".join(iqtree_command))
print("This may take some time...")

# Run IQ-TREE and let it write files in out-dir (IQ-TREE creates files with -pre)
proc = subprocess.run(iqtree_command)
if proc.returncode != 0:
    print("ERROR: IQ-TREE failed with exit code", proc.returncode)
    print("Check IQ-TREE stdout/stderr (IQ-TREE writes logs to the output directory).")
    sys.exit(proc.returncode)

tree_file = prefix + ".treefile"
log_file = prefix + ".log"

if os.path.exists(tree_file):
    print("Tree file created successfully:", tree_file)
    try:
        with open(tree_file, "r") as f:
            tree_content = f.read()
        print("Tree (first 200 chars):")
        print(tree_content[:200])
    except Exception:
        pass

    # list IQ-TREE output files
    print("\nIQ-TREE output files in", args.out_dir)
    for f in sorted(os.listdir(args.out_dir)):
        if f.startswith("lsdv_tree"):
            filepath = os.path.join(args.out_dir, f)
            size = os.path.getsize(filepath)
            print(" -", f, f"({size} bytes)")
    # attempt to print best model from log
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as lf:
                for line in lf:
                    if "Best-fit model" in line or "best-fit model" in line:
                        print("\n" + line.strip())
                        break
        except Exception:
            pass
else:
    print("ERROR: Tree file was not created. Check the IQ-TREE log in", args.out_dir)
    sys.exit(1)

print("\nDone! Next step: visualize the tree with python3 04_visualize_tree.py --tree", tree_file)
