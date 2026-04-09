#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_genome() {
    local species="$1" url="$2" filename="$3"
    local outdir="$DATA_DIR/genome/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi
    echo "  Downloading $species genome..."
    curl -L -o "$outfile.gz" "$url"
    gunzip "$outfile.gz"
    echo "  ✓ $outfile"
}

echo "=== Downloading reference genomes ==="

# Sheep — Oar_rambouillet_v1.0
download_genome "sheep" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/742/125/GCF_002742125.1_Oar_rambouillet_v1.0/GCF_002742125.1_Oar_rambouillet_v1.0_genomic.fna.gz" \
    "sheep.fa"

# Goat — ARS1 / CHIR_1.0
download_genome "goat" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/704/415/GCF_001704415.2_ARS1.2/GCF_001704415.2_ARS1.2_genomic.fna.gz" \
    "goat.fa"

echo "=== Genome downloads complete ==="
