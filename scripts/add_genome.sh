#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <species_id> <fasta_path> [assembly_name] [species_name] [scientific_name]"
    echo ""
    echo "Add a de novo genome assembly to the browser."
    echo ""
    echo "  species_id      Short identifier (e.g. 'camel', 'my_assembly')"
    echo "  fasta_path      Path to your FASTA file"
    echo "  assembly_name   Assembly name (default: species_id)"
    echo "  species_name    Display name (default: species_id)"
    echo "  scientific_name Scientific name (default: empty)"
    echo ""
    echo "Example:"
    echo "  $0 camel /path/to/camel_assembly.fa CamDro3 Camel 'Camelus dromedarius'"
    exit 1
}

[ $# -lt 2 ] && usage

SPECIES_ID="$1"
FASTA_PATH="$2"
ASSEMBLY_NAME="${3:-$SPECIES_ID}"
SPECIES_NAME="${4:-$SPECIES_ID}"
SCIENTIFIC_NAME="${5:-}"
DATA_DIR="${DATA_DIR:-data}"

# Validate input
if [ ! -f "$FASTA_PATH" ]; then
    echo "Error: FASTA file not found: $FASTA_PATH"
    exit 1
fi

GENOME_DIR="$DATA_DIR/genome/$SPECIES_ID"
FASTA_FILE="$SPECIES_ID.fa"

echo "=== Adding genome: $SPECIES_NAME ($SPECIES_ID) ==="

# Step 1: Copy FASTA
mkdir -p "$GENOME_DIR"
if [ ! -f "$GENOME_DIR/$FASTA_FILE" ]; then
    echo "  Copying FASTA..."
    cp "$FASTA_PATH" "$GENOME_DIR/$FASTA_FILE"
else
    echo "  ✓ FASTA already in place"
fi

# Step 2: Index
echo "  Indexing FASTA..."
if [ ! -f "$GENOME_DIR/$FASTA_FILE.fai" ]; then
    samtools faidx "$GENOME_DIR/$FASTA_FILE"
    echo "  ✓ .fai index created"
else
    echo "  ✓ .fai index exists"
fi

# Step 3: bgzip for JBrowse 2
if [ ! -f "$GENOME_DIR/$FASTA_FILE.gz" ]; then
    echo "  Compressing with bgzip..."
    bgzip -c "$GENOME_DIR/$FASTA_FILE" > "$GENOME_DIR/$FASTA_FILE.gz"
    samtools faidx "$GENOME_DIR/$FASTA_FILE.gz"
    echo "  ✓ bgzipped + indexed"
else
    echo "  ✓ bgzipped FASTA exists"
fi

# Step 4: Count scaffolds/chromosomes
SCAFFOLD_COUNT=$(grep -c "^>" "$GENOME_DIR/$FASTA_FILE" || true)
echo "  Found $SCAFFOLD_COUNT scaffolds/chromosomes"

# Step 5: Register in genomes.json
GENOMES_JSON="$DATA_DIR/genomes.json"
echo "  Registering in $GENOMES_JSON..."

python3 -c "
import json, os

path = '$GENOMES_JSON'
data = {}
if os.path.exists(path):
    with open(path) as f:
        data = json.load(f)

data['$SPECIES_ID'] = {
    'assembly_name': '$ASSEMBLY_NAME',
    'fasta_file': '$FASTA_FILE.gz',
    'gff_file': None,
    'qtl_bed_file': None,
    'name': '$SPECIES_NAME',
    'scientific_name': '$SCIENTIFIC_NAME',
    'chromosome_count': $SCAFFOLD_COUNT,
}

with open(path, 'w') as f:
    json.dump(data, f, indent=2)
"

echo ""
echo "=== Done! ==="
echo "  Genome registered: $SPECIES_NAME ($ASSEMBLY_NAME)"
echo "  Scaffolds: $SCAFFOLD_COUNT"
echo "  Location: $GENOME_DIR/"
echo ""
echo "  Start the browser:"
echo "    make dev-backend   # Terminal 1"
echo "    make dev-frontend  # Terminal 2"
echo "    Open http://localhost:3000"
