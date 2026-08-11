#!/bin/bash
# =============================================
# Script to build a phylogenetic tree with IQ-TREE
# This takes the aligned sequences and builds
# a maximum likelihood tree.
#
# Author: beginner bioinformatics student
# Date: 2026
# =============================================

echo "==========================================="
echo "STEP 3: Building Phylogenetic Tree"
echo "==========================================="

# check if iqtree2 is installed
if ! command -v iqtree2 &> /dev/null
then
    echo "ERROR: iqtree2 is not installed!"
    echo "Please install IQ-TREE first:"
    echo "  sudo apt install iqtree"
    echo "  OR"
    echo "  conda install -c bioconda iqtree"
    exit 1
fi

echo "IQ-TREE found at: $(which iqtree2)"
echo "IQ-TREE version:"
iqtree2 --version

# -------------------------------------------------------
# STEP 1: Check if alignment file exists
# -------------------------------------------------------
echo ""
echo "--- STEP 1: Checking input file ---"

ALIGNMENT_FILE="data/alignment/lsdv_aligned.fasta"

if [ ! -f "$ALIGNMENT_FILE" ]; then
    echo "ERROR: Alignment file not found: $ALIGNMENT_FILE"
    echo "Please run 02_run_alignment.sh first."
    exit 1
fi

echo "Alignment file found: $ALIGNMENT_FILE"
echo "Number of sequences:"
grep -c "^>" "$ALIGNMENT_FILE"

# -------------------------------------------------------
# STEP 2: Run IQ-TREE
# -------------------------------------------------------
echo ""
echo "--- STEP 2: Running IQ-TREE ---"
echo "This will take some time. IQ-TREE tests different models."
echo ""

# create output directory for tree
mkdir -p data/tree

# run IQ-TREE with these options:
# -s : the input alignment file
# -m MFP : Model Finder Plus - tests many models and picks the best one
# -bb 1000 : ultrafast bootstrap with 1000 replicates (tests tree reliability)
# -nt AUTO : automatically choose number of threads
# -pre : prefix for all output files
# -redo : redo analysis even if output exists

iqtree2 \
    -s "$ALIGNMENT_FILE" \
    -m MFP \
    -bb 1000 \
    -nt AUTO \
    -pre data/tree/lsdv_tree \
    -redo

# -------------------------------------------------------
# STEP 3: Check results
# -------------------------------------------------------
echo ""
echo "--- STEP 3: Checking results ---"

# check if the tree file was created
TREE_FILE="data/tree/lsdv_tree.treefile"

if [ -f "$TREE_FILE" ]; then
    echo "Tree file created successfully!"
    echo "Tree file: $TREE_FILE"
    echo ""
    echo "Tree file content (Newick format):"
    head -c 500 "$TREE_FILE"
    echo ""
    echo ""
    
    # show other output files
    echo "All output files from IQ-TREE:"
    ls -la data/tree/lsdv_tree.*
    
    echo ""
    echo "Best model chosen by IQ-TREE:"
    cat data/tree/lsdv_tree.log | grep "Best-fit model"
    
    echo ""
    echo "Bootstrap support values are in the tree file."
    echo "Higher values (closer to 100) mean more reliable branches."
else
    echo "ERROR: Tree file was not created!"
    echo "Check the log file: data/tree/lsdv_tree.log"
    exit 1
fi

echo ""
echo "Done! Next step: visualize the tree."
echo "Run: python3 04_visualize_tree.py"
