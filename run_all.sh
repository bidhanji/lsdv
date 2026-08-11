#!/bin/bash
# =============================================
# Run the entire LSDV phylogenetic analysis
# This script runs all steps in order.
#
# Usage: bash run_all.sh
#
# Author: beginner bioinformatics student
# Date: 2026
# =============================================

echo "============================================"
echo "  LSDV Phylogenetic Analysis Pipeline"
echo "============================================"
echo ""
echo "This script will:"
echo "  1. Download 50 LSDV genomes from NCBI"
echo "  2. Align them with MAFFT"
echo "  3. Build a phylogenetic tree with IQ-TREE"
echo "  4. Visualize the tree"
echo ""
echo "============================================"
echo ""

# record start time
START_TIME=$(date)
echo "Started at: $START_TIME"
echo ""

# -------------------------------------------------------
# STEP 1: Download genomes
# -------------------------------------------------------
echo ">>> Running Step 1: Download genomes <<<"
echo ""
python3 01_download_genomes.py
if [ $? -ne 0 ]; then
    echo "ERROR: Step 1 failed!"
    exit 1
fi
echo ""
echo ">>> Step 1 complete <<<"
echo ""

# -------------------------------------------------------
# STEP 2: Run alignment
# -------------------------------------------------------
echo ">>> Running Step 2: MAFFT alignment <<<"
echo ""
bash 02_run_alignment.sh
if [ $? -ne 0 ]; then
    echo "ERROR: Step 2 failed!"
    exit 1
fi
echo ""
echo ">>> Step 2 complete <<<"
echo ""

# -------------------------------------------------------
# STEP 3: Build tree
# -------------------------------------------------------
echo ">>> Running Step 3: IQ-TREE <<<"
echo ""
bash 03_run_iqtree.sh
if [ $? -ne 0 ]; then
    echo "ERROR: Step 3 failed!"
    exit 1
fi
echo ""
echo ">>> Step 3 complete <<<"
echo ""

# -------------------------------------------------------
# STEP 4: Visualize tree
# -------------------------------------------------------
echo ">>> Running Step 4: Visualize tree <<<"
echo ""
python3 04_visualize_tree.py
if [ $? -ne 0 ]; then
    echo "ERROR: Step 4 failed!"
    exit 1
fi
echo ""
echo ">>> Step 4 complete <<<"

# -------------------------------------------------------
# Done!
# -------------------------------------------------------
echo ""
echo "============================================"
echo "  ALL DONE!"
echo "============================================"
END_TIME=$(date)
echo "Started at: $START_TIME"
echo "Finished at: $END_TIME"
echo ""
echo "Output files:"
echo "  data/genomes/          - Downloaded FASTA files"
echo "  data/alignment/        - MAFFT alignment"
echo "  data/tree/             - IQ-TREE output and tree images"
echo ""
echo "Tree images:"
echo "  data/tree/lsdv_phylogenetic_tree.png"
echo "  data/tree/lsdv_phylogenetic_tree.svg"
echo ""
echo "Thanks for using this pipeline! :)"
