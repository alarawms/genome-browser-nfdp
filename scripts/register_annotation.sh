#!/usr/bin/env bash
# Register a new gene-annotation GFF as a track for a species.
#
#   scripts/register_annotation.sh <species_id> <track_slug> "<track_label>" <gff_path> [--primary]
#
# What it does:
#   1. Sort + bgzip + tabix the GFF via Docker (genome-browser-data image)
#      -> data/annotations/<species_id>/<species_id>.<track_slug>.sorted.gff3.gz
#   2. Atomically update data/genomes.json:
#        - --primary: set as 'gff_file'; push the old primary (if any) into extra_gene_tracks
#        - default:   append {file, label} to extra_gene_tracks
#      De-duplicates by filename so re-registrations are idempotent.
#
# Examples:
#   scripts/register_annotation.sh najdi braker3 "Genes (BRAKER3 de novo)" /tmp/braker3.gff3
#   scripts/register_annotation.sh najdi gemoma "Genes (GeMoMa)" /tmp/gemoma.gff3 --primary

set -euo pipefail

if [ $# -lt 4 ]; then
    echo "Usage: $0 <species_id> <track_slug> \"<track_label>\" <gff_path> [--primary]"
    exit 1
fi

SPECIES="$1"
SLUG="$2"
LABEL="$3"
GFF="$4"
MAKE_PRIMARY="no"
[ "${5:-}" = "--primary" ] && MAKE_PRIMARY="yes"

DATA_DIR="${DATA_DIR:-data}"
OUT_DIR="$DATA_DIR/annotations/$SPECIES"
OUT_NAME="${SPECIES}.${SLUG}.sorted.gff3.gz"
OUT_PATH="$OUT_DIR/$OUT_NAME"

if [ ! -f "$GFF" ]; then
    echo "✗ GFF not found: $GFF"
    exit 1
fi
mkdir -p "$OUT_DIR"

echo "=== Register annotation: $SPECIES / $SLUG ==="
echo "  source:   $GFF"
echo "  output:   $OUT_PATH"
echo "  label:    $LABEL"
echo "  primary:  $MAKE_PRIMARY"
echo ""

# --- Step 1: sort + bgzip + tabix via Docker -------------------------------
echo "--- sorting + bgzipping + indexing ($(grep -vc "^#" "$GFF" 2>/dev/null || echo ?) feature lines) ---"
docker run --rm --user "$(id -u):$(id -g)" \
    -v "$(realpath .)":/work \
    -v "$(realpath "$(dirname "$GFF")")":/src:ro \
    -v /tmp:/tmp \
    -w /work --entrypoint bash genome-browser-data \
    -c "awk '!/^#/' /src/$(basename "$GFF") | sort -T /tmp -k1,1 -k4,4n | bgzip > /work/$OUT_PATH \
     && tabix -p gff /work/$OUT_PATH \
     && ls -lh /work/$OUT_PATH"

# --- Step 2: update genomes.json (atomic, idempotent) ----------------------
echo ""
echo "--- updating $DATA_DIR/genomes.json ---"
GENOMES_JSON="$DATA_DIR/genomes.json"
[ ! -f "$GENOMES_JSON" ] && echo "{}" > "$GENOMES_JSON"

python3 - "$GENOMES_JSON" "$SPECIES" "$OUT_NAME" "$LABEL" "$MAKE_PRIMARY" <<'PYEOF'
import json, sys
from pathlib import Path

path = Path(sys.argv[1])
species, new_file, new_label, make_primary = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == "yes"

data = json.loads(path.read_text())
entry = data.setdefault(species, {})
extras = entry.setdefault("extra_gene_tracks", [])

# Drop any existing entry for this file (idempotent)
extras = [e for e in extras if e.get("file") != new_file]

if make_primary:
    # Demote old primary (if any) into extras
    old_primary = entry.get("gff_file")
    old_label = entry.get("gff_track_label", "Genes")
    if old_primary and old_primary != new_file:
        extras.append({"file": old_primary, "label": old_label})
    entry["gff_file"] = new_file
    entry["gff_track_label"] = new_label
else:
    # Promote in-extras if we were already primary
    if entry.get("gff_file") == new_file:
        entry["gff_track_label"] = new_label
    else:
        extras.append({"file": new_file, "label": new_label})

entry["extra_gene_tracks"] = extras
path.write_text(json.dumps(data, indent=2) + "\n")
print(f"  ✓ {species} now has gff_file='{entry.get('gff_file','<none>')}' + {len(extras)} extra_gene_tracks:")
for e in extras:
    print(f"      - {e['file']}   ({e['label']})")
PYEOF

echo ""
echo "=== Done ==="
if [ "$MAKE_PRIMARY" = "yes" ]; then
    echo "  Recompute QTL overlaps against the new primary:"
    echo "    python3 scripts/compute_qtl_gene_overlap.py $DATA_DIR/qtl/$SPECIES/qtls.json $OUT_PATH"
fi
echo "  Reload backend:"
echo "    touch src/backend/data_loader.py"
echo "  Hard-refresh browser to see the new track."
