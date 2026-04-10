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
    curl -fL -o "$outfile" "$url"
    # QTLdb may return gzipped files — decompress if needed
    if file "$outfile" | grep -q "gzip"; then
        echo "  Decompressing..."
        mv "$outfile" "$outfile.gz"
        gunzip "$outfile.gz"
    fi
    # Validate: should contain tab-separated GFF lines
    if head -20 "$outfile" | grep -q "^<"; then
        echo "  ✗ Download failed — received HTML instead of GFF. Check URL."
        rm -f "$outfile"
        return 1
    fi
    echo "  ✓ $outfile"
}

echo "=== Downloading QTL data from Animal QTLdb ==="

# Sheep QTLs — GFF from Animal QTLdb (OAR_rambo2 build, release 58)
# NOTE: QTLdb uses tokenized URLs that may change with new releases.
# If download fails, visit https://www.animalgenome.org/QTLdb/OA/index
# and download the GFF file for OAR_rambo2 manually to data/qtl/sheep/sheep_qtldb.gff
download_qtl "sheep" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/OA/download?f=Y660yclWWas47TpwiMBql&c=26090410" \
    "sheep_qtldb.gff"

# Goat QTLs — GFF from Animal QTLdb (CHIR_ARS1 build, release 58)
# If download fails, visit https://www.animalgenome.org/QTLdb/CH/index
download_qtl "goat" \
    "https://www.animalgenome.org/cgi-bin/QTLdb/CH/download?f=ZyQN21BMus0RqtabmIOuJ&c=26090410" \
    "goat_qtldb.gff"

echo "=== QTL downloads complete ==="
