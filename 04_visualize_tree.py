#!/usr/bin/env python3
"""
Script to visualize the phylogenetic tree from IQ-TREE.

Uses matplotlib + Bio.Phylo. Works headless (Agg) so it can run on servers.
Author: improved for portability
Date: 2026
"""
import os
import argparse
import sys

parser = argparse.ArgumentParser(description="Visualize a Newick tree (IQ-TREE output)")
parser.add_argument("--tree", "-t", default="data/tree/lsdv_tree.treefile",
                    help="Path to the IQ-TREE .treefile")
parser.add_argument("--out-dir", "-o", default="data/tree",
                    help="Directory to write images (PNG, SVG)")
parser.add_argument("--png", default="lsdv_phylogenetic_tree.png",
                    help="PNG filename to write (in out-dir)")
parser.add_argument("--svg", default="lsdv_phylogenetic_tree.svg",
                    help="SVG filename to write (in out-dir)")
args = parser.parse_args()

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: matplotlib is required. Install via: pip install matplotlib")
    print("or: pip install -r requirements.txt")
    sys.exit(1)

try:
    from Bio import Phylo
except ImportError:
    print("ERROR: Biopython is required. Install via: pip install biopython")
    print("or: pip install -r requirements.txt")
    sys.exit(1)

if not os.path.exists(args.tree):
    print("ERROR: Tree file not found:", args.tree)
    print("Please run python3 03_run_iqtree.py and point --out-dir to where IQ-TREE wrote the tree.")
    sys.exit(1)

print("Loading tree from:", args.tree)
tree = Phylo.read(args.tree, "newick")

print("Number of terminals (tips):", len(tree.get_terminals()))
print("Number of clades:", len(list(tree.find_clades())))

print("\n--- Cleaning up leaf names ---")
for clade in tree.get_terminals():
    old_name = clade.name
    if not old_name:
        continue
    new_name = old_name.split(".1")[0] if ".1" in old_name else old_name
    if "ENA|" in new_name:
        new_name = new_name.replace("ENA|", "").split("|")[-1]
    if len(new_name) > 15:
        new_name = new_name[:15]
    clade.name = new_name
    # Print a short mapping for debugging
    print(" ", (old_name[:40] if old_name else ""), "->", new_name)

print("\n--- Drawing tree ---")
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
Phylo.draw(tree, axes=ax, do_show=False)
ax.set_title("LSDV Phylogenetic Tree (Maximum Likelihood)", fontsize=14, fontweight='bold')
ax.set_xlabel("Branch length", fontsize=11)

os.makedirs(args.out_dir, exist_ok=True)
png_output = os.path.join(args.out_dir, args.png)
svg_output = os.path.join(args.out_dir, args.svg)

plt.savefig(png_output, dpi=300, bbox_inches='tight', facecolor='white')
print("Saved PNG:", png_output)
plt.savefig(svg_output, bbox_inches='tight', facecolor='white')
print("Saved SVG:", svg_output)
plt.close()

print("\n--- Text representation of tree ---")
Phylo.draw_ascii(tree)

print("\nDone! Check the tree images in", args.out_dir)
