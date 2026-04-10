import json
from pathlib import Path

# Built-in species (always available)
_BUILTIN_SPECIES_META = {
    "sheep": {
        "assembly_name": "ARS-UI_Ramb_v2.0",
        "fasta_file": "sheep.fa.gz",
        "gff_file": "sheep.sorted.gff3.gz",
        "qtl_bed_file": "sheep_qtls.sorted.bed.gz",
    },
    "goat": {
        "assembly_name": "CHIR_1.0",
        "fasta_file": "goat.fa.gz",
        "gff_file": "goat.sorted.gff3.gz",
        "qtl_bed_file": "goat_qtls.sorted.bed.gz",
    },
}


def _load_species_meta(data_dir: str | None = None) -> dict:
    """Load built-in species + any user-added genomes from data/genomes.json."""
    meta = dict(_BUILTIN_SPECIES_META)
    if data_dir:
        genomes_json = Path(data_dir) / "genomes.json"
        if genomes_json.exists():
            with open(genomes_json) as f:
                meta.update(json.load(f))
    return meta


def get_species_meta(data_dir: str | None = None) -> dict:
    return _load_species_meta(data_dir)


def make_assembly_config(species_id: str, base_url: str, data_dir: str | None = None) -> dict:
    meta = _load_species_meta(data_dir)[species_id]
    genome_url = f"{base_url}/genome/{species_id}"
    return {
        "name": meta["assembly_name"],
        "sequence": {
            "type": "ReferenceSequenceTrack",
            "trackId": f"{species_id}-reference",
            "adapter": {
                "type": "BgzipFastaAdapter",
                "fastaLocation": {"uri": f"{genome_url}/{meta['fasta_file']}"},
                "faiLocation": {"uri": f"{genome_url}/{meta['fasta_file']}.fai"},
                "gziLocation": {"uri": f"{genome_url}/{meta['fasta_file']}.gzi"},
            },
        },
    }


def make_track_configs(species_id: str, base_url: str, data_dir: str | None = None) -> list[dict]:
    meta = _load_species_meta(data_dir)[species_id]
    assembly_name = meta["assembly_name"]
    tracks = []

    # Gene annotations (optional — de novo genomes may not have these)
    if meta.get("gff_file"):
        ann_url = f"{base_url}/annotations/{species_id}"
        tracks.append({
            "type": "FeatureTrack",
            "trackId": f"{species_id}-genes",
            "name": "Gene Annotations",
            "assemblyNames": [assembly_name],
            "adapter": {
                "type": "Gff3TabixAdapter",
                "gffGzLocation": {"uri": f"{ann_url}/{meta['gff_file']}"},
                "index": {
                    "location": {"uri": f"{ann_url}/{meta['gff_file']}.tbi"},
                },
            },
        })

    # QTL track (optional)
    if meta.get("qtl_bed_file"):
        qtl_url = f"{base_url}/qtl/{species_id}"
        tracks.append({
            "type": "FeatureTrack",
            "trackId": f"{species_id}-qtls",
            "name": "QTLs",
            "assemblyNames": [assembly_name],
            "adapter": {
                "type": "BedTabixAdapter",
                "bedGzLocation": {"uri": f"{qtl_url}/{meta['qtl_bed_file']}"},
                "index": {
                    "location": {
                        "uri": f"{qtl_url}/{meta['qtl_bed_file']}.tbi"
                    },
                },
            },
        })

    return tracks
