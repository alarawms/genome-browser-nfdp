#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-data}"

download_qtl() {
    local species="$1" url="$2" filename="$3"
    local outdir="$DATA_DIR/qtl/$species"
    local outfile="$outdir/$filename"

    mkdir -p "$outdir"
    if [ -f "$outfile" ]; then
        echo "  ✓ $outfile already exists, skipping"
        return
    fi
    echo "  Downloading $species QTL data..."
    curl -L -o "$outfile" "$url"
    echo "  ✓ $outfile"
}

echo "=== Downloading QTL data from Animal QTLdb ==="

# Sheep QTLs — GFF format from Animal QTLdb
download_qtl "sheep" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/OA/downloaddatfile?TYPE=gff&FILEID=1" \
    "sheep_qtldb.gff"

# Goat QTLs — GFF format from Animal QTLdb
download_qtl "goat" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/CH/downloaddatfile?TYPE=gff&FILEID=1" \
    "goat_qtldb.gff"

echo "=== QTL downloads complete ==="
