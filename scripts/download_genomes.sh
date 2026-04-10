#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_genome() {
    local species="$1" accession="$2"
    local outdir="$DATA_DIR/genome/$species"
    local outfile="$outdir/$species.fa"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi

    echo "  Downloading $species genome ($accession) via NCBI datasets..."
    local tmpdir
    tmpdir=$(mktemp -d)

    datasets download genome accession "$accession" \
        --include genome \
        --filename "$tmpdir/genome.zip"

    unzip -q -o "$tmpdir/genome.zip" -d "$tmpdir"
    # Find the FASTA file in the extracted data
    local fasta
    fasta=$(find "$tmpdir/ncbi_dataset/data" -name "*.fna" | head -1)

    if [ -z "$fasta" ]; then
        echo "  ✗ No FASTA found in download"
        rm -rf "$tmpdir"
        return 1
    fi

    cp "$fasta" "$outfile"
    rm -rf "$tmpdir"
    echo "  ✓ $outfile"
}

echo "=== Downloading reference genomes ==="

# Sheep — ARS-UI_Ramb_v3.0 (latest NCBI reference)
download_genome "sheep" "GCF_016772045.2"

# Goat — ARS1.2
download_genome "goat" "GCF_001704415.2"

echo "=== Genome downloads complete ==="
