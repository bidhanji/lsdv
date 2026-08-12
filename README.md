# LSDV Phylogenetic Analysis

This project downloads Lumpy Skin Disease Virus (LSDV) genomes from ENA (European Nucleotide Archive), aligns them with MAFFT, builds a phylogenetic tree with IQ-TREE, and visualizes it.

## What is this?

Lumpy Skin Disease is a viral disease that affects cattle. It is caused by Lumpy Skin Disease Virus (LSDV), which belongs to the Poxviridae family.

This pipeline:
1. Downloads LSDV complete genomes from ENA using Python
2. Aligns them with MAFFT (multiple sequence alignment)
3. Builds a phylogenetic tree with IQ-TREE (maximum likelihood method)
4. Visualizes the tree with matplotlib

## Installation / prerequisites

Python packages:
- Install the Python deps listed in requirements.txt:
  ```bash
  pip install -r requirements.txt   

## Requirements

You need these software installed:

- **Python 3** (with Biopython, matplotlib)
- **MAFFT** (for sequence alignment)
- **IQ-TREE 2** (for phylogenetic tree building)

### Install Python packages

```bash
pip install biopython matplotlib
```

### Install MAFFT

```bash
# Ubuntu/Debian
sudo apt install mafft

# OR with conda
conda install -c bioconda mafft
```

### Install IQ-TREE

```bash
# Ubuntu/Debian
sudo apt install iqtree

# OR with conda
conda install -c bioconda iqtree
```

## How to run

### Option 1: Run everything at once

```bash
python3 run_all.py
```

### Option 2: Run each step separately

**Step 1: Download genomes**
```bash
python3 01_download_genomes.py
```

**Step 2: Align sequences**
```bash
python3 02_run_alignment.py
```

**Step 3: Build phylogenetic tree**
```bash
python3 03_run_iqtree.py
```

**Step 4: Visualize tree**
```bash
python3 04_visualize_tree.py
```

## Output files

```
data/
├── genomes/                    # Downloaded FASTA files
├── alignment/
│   ├── subset_combined.fasta   # Combined sequences
│   └── lsdv_aligned.fasta      # MAFFT alignment result
└── tree/
    ├── lsdv_tree.treefile      # The phylogenetic tree (Newick format)
    ├── lsdv_tree.log           # IQ-TREE log file
    ├── lsdv_phylogenetic_tree.png  # Tree image (PNG)
    └── lsdv_phylogenetic_tree.svg  # Tree image (SVG)
```

## Understanding the tree

- **Leaves (tips)**: Each tip is one LSDV genome, labeled with its ENA accession number
- **Branch lengths**: Represent evolutionary distance
- **Bootstrap support values**: Numbers on branches (0-100) indicate reliability

## Notes

- We use ENA instead of NCBI because NCBI blocks automated requests from cloud servers
- The download script tries many accessions because some may fail (timeouts) or be partial sequences
- Only complete genomes (>100K bp) are used for the alignment
- MAFFT alignment of whole genomes takes significant time (~10-15 minutes for 12 genomes)

## References

- MAFFT: Katoh et al. (2002) Nucleic Acids Research
- IQ-TREE: Minh et al. (2020) Molecular Biology and Evolution
- ENA: https://www.ebi.ac.uk/ena

## Author

This pipeline was written by me a recent BVsc&AH graduate and a beginner who is learning biopython as a learning exercise.

## License

This project is for educational purposes. Use freely.
