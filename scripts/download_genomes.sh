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
    curl -fL -o "$outfile.gz" "$url"
    # Validate: must be gzip
    if ! file "$outfile.gz" | grep -q "gzip"; then
        echo "  ✗ Download failed — not a valid gzip file. Check URL."
        rm -f "$outfile.gz"
        return 1
    fi
    gunzip "$outfile.gz"
    echo "  ✓ $outfile"
}

echo "=== Downloading reference genomes ==="

# Sheep — ARS-UI_Ramb_v2.0 (current Ensembl/NCBI reference)
download_genome "sheep" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/016/772/045/GCF_016772045.2_ARS-UI_Ramb_v2.0/GCF_016772045.2_ARS-UI_Ramb_v2.0_genomic.fna.gz" \
    "sheep.fa"

# Goat — ARS1.2
download_genome "goat" \
    "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/001/704/415/GCF_001704415.2_ARS1.2/GCF_001704415.2_ARS1.2_genomic.fna.gz" \
    "goat.fa"

echo "=== Genome downloads complete ==="
