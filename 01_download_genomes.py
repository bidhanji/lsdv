#!/usr/bin/env python3
"""
Script to download LSDV genomes from ENA (European Nucleotide Archive).

We try to download as many complete LSDV genomes as possible.
Some accessions might fail (timeouts) or be partial sequences,
so we keep trying until we have enough.

NOTE: NCBI blocks automated requests from cloud servers,
so we use ENA instead. ENA is the European mirror of GenBank.

FIXES applied vs original:
  1. Accession-match verification: the FASTA header returned by ENA is now
     checked against the accession we actually requested. If ENA returns
     something else (wrong record, redirect, error page disguised as
     FASTA), the script now rejects it instead of silently saving it.
  2. Retry logic: each accession gets up to --retries attempts (default 3)
     with an exponential backoff, instead of one shot. Network blips no
     longer permanently sink an accession.
  3. Existing-file re-validation: files already on disk from a previous
     run are no longer blindly trusted as "already downloaded". They are
     re-parsed and checked for a valid header + non-zero sequence before
     being counted — a truncated file from an interrupted run gets
     re-downloaded instead of silently counted as complete forever.

Author: Bidhan Koirala
Date: 2026
"""

import urllib.request
import urllib.error
import os
import time
import argparse
import sys

parser = argparse.ArgumentParser(description="Download LSDV genomes from ENA")
parser.add_argument("--output", "-o", default="data/genomes",
                     help="output folder for downloaded FASTA files")
parser.add_argument("--target", "-t", type=int, default=50,
                     help="target number of genomes to download (complete/near-complete)")
parser.add_argument("--retries", type=int, default=3,
                     help="number of attempts per accession before giving up")
parser.add_argument("--retry-backoff", type=float, default=2.0,
                     help="base seconds to wait between retries (doubles each attempt)")
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
# Helpers
# -------------------------------------------------------
def parse_header_accession(header_line):
    """
    Extract the accession-like token from a FASTA header, e.g.
    '>ENA|AF325528|AF325528.1 Lumpy skin disease virus...' -> 'AF325528'
    ENA headers vary in format, so we just check the requested accession
    appears as a substring token of the header (case-insensitive), rather
    than requiring an exact positional match. This is deliberately a bit
    loose because ENA header formatting is not perfectly consistent, but
    it is enough to catch the failure mode that actually matters: getting
    back a completely different, unrelated record.
    """
    return header_line.upper()


def accession_matches(requested_acc, header_line):
    return requested_acc.upper() in parse_header_accession(header_line)


def validate_fasta_content(fasta_text, requested_acc):
    """
    Returns (is_valid, seq_len, reason).
    Checks: starts with '>', header contains requested accession,
    and sequence length > 0.
    """
    if not fasta_text or not fasta_text.startswith(">"):
        return False, 0, "not FASTA (no '>' header)"

    lines = fasta_text.split("\n")
    header_line = lines[0]

    if not accession_matches(requested_acc, header_line):
        return False, 0, f"header does not mention requested accession ({header_line[:80]!r})"

    seq_lines = [l for l in lines if not l.startswith(">") and len(l) > 0]
    seq_len = sum(len(l) for l in seq_lines)

    if seq_len == 0:
        return False, 0, "zero-length sequence"

    return True, seq_len, "ok"


def download_accession(acc, retries, backoff):
    """
    Attempt to download one accession, retrying on failure.
    Returns (fasta_text_or_None, seq_len, error_message_or_None).
    """
    url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + acc
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "lsdv-downloader/1.1 (+https://github.com/bidhanji/lsdv)")
            with urllib.request.urlopen(req, timeout=20) as response:
                fasta = response.read().decode("utf-8")

            is_valid, seq_len, reason = validate_fasta_content(fasta, acc)
            if is_valid:
                return fasta, seq_len, None
            else:
                last_error = reason
                # a bad response (e.g. wrong record) is worth retrying too —
                # could be a transient mirror/proxy issue
        except Exception as e:
            last_error = str(e)[:200]

        if attempt < retries:
            wait = backoff * (2 ** (attempt - 1))
            print(f" ... attempt {attempt}/{retries} failed ({last_error}), retrying in {wait:.1f}s", end="")
            time.sleep(wait)
        else:
            time.sleep(0.3)  # be polite before moving to next accession

    return None, 0, last_error


def existing_file_is_valid(filepath, acc):
    """Re-validate a file left over from a previous run instead of trusting it blindly."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except Exception:
        return False, 0

    is_valid, seq_len, reason = validate_fasta_content(content, acc)
    return is_valid, seq_len


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

    filepath = os.path.join(output_folder, acc + ".fasta")

    # FIX #3: re-validate existing files instead of trusting them blindly
    if os.path.exists(filepath):
        is_valid, seq_len = existing_file_is_valid(filepath, acc)
        if is_valid:
            print(f"[{downloaded_count + 1}/{target}] {acc} already exists and is valid ({seq_len} bp), skipping")
            downloaded_count += 1
            continue
        else:
            print(f"[{downloaded_count + 1}/{target}] {acc} exists but is invalid/corrupted — re-downloading")
            # fall through to re-download

    print(f"[{downloaded_count + 1}/{target}] Downloading: {acc}", end="")

    fasta, seq_len, error = download_accession(acc, args.retries, args.retry_backoff)

    if fasta is not None:
        with open(filepath, "w") as f:
            f.write(fasta)
        downloaded_count += 1
        print(" ... OK (" + str(seq_len) + " bp, accession verified)")
    else:
        print(" ... FAILED after", args.retries, "attempts:", error)
        failed_count += 1

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

print("\nGenomes (sorted by size):")
file_sizes = []
for f in fasta_files:
    filepath = os.path.join(output_folder, f)
    with open(filepath) as fh:
        content = fh.read()
    seq_len = sum(len(l) for l in content.split("\n")
                  if not l.startswith(">") and len(l) > 0)
    file_sizes.append((f, seq_len))

file_sizes.sort(key=lambda x: x[1], reverse=True)
for f, slen in file_sizes:
    marker = " [COMPLETE]" if slen > 100000 else ""
    print(" -", f, "(" + str(slen) + " bp)" + marker)

complete_count = sum(1 for _, s in file_sizes if s > 100000)
print("\nComplete genomes (>100K bp):", complete_count)
print("Total genomes:", len(fasta_files))

if len(fasta_files) >= 2:
    print("\nReady for alignment! Run: python3 02_run_alignment.py")
else:
    print("\nNot enough genomes. Check your connection.")
