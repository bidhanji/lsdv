#!/usr/bin/env python3
"""
Script to visualize the phylogenetic tree from IQ-TREE.
Uses matplotlib + Bio.Phylo instead of ete3 (which needs PyQt).

Author: Bidhan Koirala
Date: 8/12/2026
"""

# import what we need
import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from Bio import Phylo

# -------------------------------------------------------
# STEP 1: Load the tree file
# -------------------------------------------------------
print("===========================================")
print("STEP 4: Visualizing the Phylogenetic Tree")
print("===========================================")
print("")

tree_file = "data/tree/lsdv_tree.treefile"

if not os.path.exists(tree_file):
    print("ERROR: Tree file not found:", tree_file)
    print("Please run 03_run_iqtree.sh first.")
    exit(1)

print("Loading tree from:", tree_file)

# load the tree using Bio.Phylo
tree = Phylo.read(tree_file, "newick")

# print some info
print("Number of terminals (tips):", len(tree.get_terminals()))
print("Number of clades:", len(list(tree.find_clades())))

# -------------------------------------------------------
# STEP 2: Clean up the leaf names
# -------------------------------------------------------
print("\n--- Cleaning up leaf names ---")

for clade in tree.get_terminals():
    old_name = clade.name
    # shorten the name - just keep the accession number
    new_name = old_name.split(".1")[0] if ".1" in old_name else old_name
    new_name = new_name.replace("ENA|", "").split("|")[-1] if "ENA|" in new_name else new_name
    # keep first 15 chars max
    if len(new_name) > 15:
        new_name = new_name[:15]
    clade.name = new_name
    print("  ", old_name[:40], "->", new_name)

# -------------------------------------------------------
# STEP 3: Draw the tree
# -------------------------------------------------------
print("\n--- Drawing tree ---")

# create a figure
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

# draw the tree
Phylo.draw(tree, axes=ax, do_show=False)

# add title
ax.set_title("LSDV Phylogenetic Tree (Maximum Likelihood)", fontsize=14, fontweight='bold')
ax.set_xlabel("Branch length", fontsize=11)

# -------------------------------------------------------
# STEP 4: Save the tree image
# -------------------------------------------------------
print("\n--- Saving tree image ---")

os.makedirs("data/tree", exist_ok=True)

# save as PNG
png_output = "data/tree/lsdv_phylogenetic_tree.png"
plt.savefig(png_output, dpi=300, bbox_inches='tight', facecolor='white')
print("Saved PNG:", png_output)

# save as SVG
svg_output = "data/tree/lsdv_phylogenetic_tree.svg"
plt.savefig(svg_output, bbox_inches='tight', facecolor='white')
print("Saved SVG:", svg_output)

plt.close()

# -------------------------------------------------------
# STEP 5: Print tree in text format
# -------------------------------------------------------
print("\n--- Text representation of tree ---")
Phylo.draw_ascii(tree)

print("\nDone! Check the tree images in data/tree/")
print("Files created:")
print("  -", png_output)
print("  -", svg_output)
