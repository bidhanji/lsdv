#!/usr/bin/env python3
"""
Run the entire LSDV phylogenetic analysis.
This script runs all steps in order.

Usage: python3 run_all.py

Author: beginner bioinformatics student
Date: 2026
"""

# import what we need
import subprocess
import time

print("============================================")
print("  LSDV Phylogenetic Analysis Pipeline")
print("============================================")
print("")
print("This script will:")
print("  1. Download LSDV genomes from ENA")
print("  2. Align them with MAFFT")
print("  3. Build a phylogenetic tree with IQ-TREE")
print("  4. Visualize the tree")
print("")
print("============================================")
print("")

# record start time
start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print("Started at:", start_time)
print("")

# -------------------------------------------------------
# helper function to run a step
# -------------------------------------------------------
def run_step(step_name, script_name):
    """Run a Python script and check if it succeeded."""
    print(">>> Running:", step_name, "<<<")
    print("")

    # run the script
    result = subprocess.run(["python3", script_name])

    # check if it worked
    if result.returncode != 0:
        print("")
        print("ERROR:", step_name, "failed!")
        exit(1)

    print("")
    print(">>>", step_name, "complete <<<")
    print("")

# -------------------------------------------------------
# STEP 1: Download genomes
# -------------------------------------------------------
run_step("Step 1: Download genomes", "01_download_genomes.py")

# -------------------------------------------------------
# STEP 2: Run alignment
# -------------------------------------------------------
run_step("Step 2: MAFFT alignment", "02_run_alignment.py")

# -------------------------------------------------------
# STEP 3: Build tree
# -------------------------------------------------------
run_step("Step 3: IQ-TREE", "03_run_iqtree.py")

# -------------------------------------------------------
# STEP 4: Visualize tree
# -------------------------------------------------------
run_step("Step 4: Visualize tree", "04_visualize_tree.py")

# -------------------------------------------------------
# Done!
# -------------------------------------------------------
end_time = time.strftime("%Y-%m-%d %H:%M:%S")
print("============================================")
print("  ALL DONE!")
print("============================================")
print("Started at:", start_time)
print("Finished at:", end_time)
print("")
print("Output files:")
print("  data/genomes/          - Downloaded FASTA files")
print("  data/alignment/        - MAFFT alignment")
print("  data/tree/             - IQ-TREE output and tree images")
print("")
print("Tree images:")
print("  data/tree/lsdv_phylogenetic_tree.png")
print("  data/tree/lsdv_phylogenetic_tree.svg")
print("")
print("Thanks for using this pipeline! :)")
