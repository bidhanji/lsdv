#!/usr/bin/env python3
"""
Script to download LSDV genomes from ENA (European Nucleotide Archive).

We try to download as many complete LSDV genomes as possible.
Some accessions might fail (timeouts) or be partial sequences,
so we keep trying until we have enough.

NOTE: NCBI blocks automated requests from cloud servers,
so we use ENA instead. ENA is the European mirror of GenBank.

Author: Bidhan Koirala
Date: 2026
"""

import urllib.request
import os
import time
import argparse
import sys

# Allow overriding output folder and target via CLI so the script is portable
parser = argparse.ArgumentParser(description="Download LSDV genomes from ENA")
parser.add_argument("--output", "-o", default="data/genomes",
                    help="output folder for downloaded FASTA files")
parser.add_argument("--target", "-t", type=int, default=50,
                    help="target number of genomes to download (complete/near-complete)")
args = parser.parse_args()

output_folder = args.output
if not os.path.exists(output_folder):
    os.makedirs(output_folder, exist_ok=True)
    print("Created folder:", output_folder)

# -------------------------------------------------------
# List of known LSDV genome accession numbers
# From published papers and databases
# We have more than 50 in case some fail
# -------------------------------------------------------
accession_list = [
    # Complete genomes (~150K bp)
    "AF325528", "AF409137", "AF409138", "KX764643", "KX764644",
    "KX764645", "HQ849551", "OL752713", "PV022135", "PP979138",
    "PP145892", "PQ878211",
    # Near-complete and large partial genomes
    "MN693049", "MN693048", "MN693047", "MT778646", "MT778647", "MT778649",
    "MW881893",
    # Additional accessions (might be partial)
    "OP123486", "OP123487", "OP123488", "OP123489", "OP123490",
    "OP123491", "OP123492", "OP123493", "OP123494",
    "KY829029", "KY829030", "KY829031",
    "KU975497", "KU975498", "KU975499",
    "KT355931", "KT355932",
    "KP063704", "KP063705",
    "KF188440", "KF188441",
    "JQ995147", "JQ995148",
    "HQ849550", "GU119941", "GU119942",
    "FJ869360", "FJ869361",
    "EU625262", "EU625263",
    "DQ087512", "DQ087513",
    "AY130487", "AY130488",
    "AF409139",
    "MK495963", "MK495964",
    "MH646680", "MH646681",
    "MG646577", "MF598537", "MF598538", "MF598539",
    "MN072715", "MW355914", "MW355915",
    "MW881892",
    "OL752712", "OL752714",
]

print("Total accessions to try:", len(accession_list))
print(f"Target: {args.target} genomes (complete or near-complete)")

# -------------------------------------------------------
# Download genomes
# -------------------------------------------------------
print("\n--- Downloading genomes from ENA ---")

downloaded_count = 0
failed_count = 0
target = args.target

for i, acc in enumerate(accession_list):
    if downloaded_count >= target:
        print("Reached target of", target, "genomes! Stopping.")
        break

    # skip if we already have this one
    filepath = os.path.join(output_folder, acc + ".fasta")
    if os.path.exists(filepath):
        print(f"[{downloaded_count + 1}/{target}] {acc} already exists, skipping")
        downloaded_count += 1
        continue

    url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + acc

    print(f"[{downloaded_count + 1}/{target}] Downloading: {acc}", end="")

    try:
        req = urllib.request.Request(url)
        # Use a friendly User-Agent and include script name so mirrors can identify us
        req.add_header("User-Agent", "lsdv-downloader/1.0 (+https://github.com/bidhanji/lsdv)")
        with urllib.request.urlopen(req, timeout=20) as response:
            fasta = response.read().decode("utf-8")

        if fasta.startswith(">"):
            # count sequence length
            seq_lines = [l for l in fasta.split("\n")
                         if not l.startswith(">") and len(l) > 0]
            seq_len = sum(len(l) for l in seq_lines)

            with open(filepath, "w") as f:
                f.write(fasta)
            downloaded_count += 1
            print(" ... OK (" + str(seq_len) + " bp)")
        else:
            print(" ... not FASTA")
            failed_count += 1

        # be polite to the ENA mirror
        time.sleep(0.3)

    except Exception as e:
        # show only short error
        print(" ... FAILED:", str(e)[:200])
        failed_count += 1
        time.sleep(0.3)

# -------------------------------------------------------
# Summary
# -------------------------------------------------------
print("\n" + "=" * 50)
print("DOWNLOAD SUMMARY")
print("=" * 50)

fasta_files = [f for f in os.listdir(output_folder) if f.endswith(".fasta")]
print("Total FASTA files:", len(fasta_files))
print("Downloaded in this run:", downloaded_count)
print("Failed:", failed_count)

# show what we have
print("\nGenomes (sorted by size):")
file_sizes = []
for f in fasta_files:
    filepath = os.path.join(output_folder, f)
    # count actual sequence length
    with open(filepath) as fh:
        content = fh.read()
    seq_len = sum(len(l) for l in content.split("\n")
                  if not l.startswith(">") and len(l) > 0)
    file_sizes.append((f, seq_len))

file_sizes.sort(key=lambda x: x[1], reverse=True)
for f, slen in file_sizes:
    marker = " [COMPLETE]" if slen > 100000 else ""
    print("  -", f, "(" + str(slen) + " bp)" + marker)

complete_count = sum(1 for _, s in file_sizes if s > 100000)
print("\nComplete genomes (>100K bp):", complete_count)
print("Total genomes:", len(fasta_files))

if len(fasta_files) >= 2:
    print("\nReady for alignment! Run: python3 02_run_alignment.py")
else:
    print("\nNot enough genomes. Check your connection.")
