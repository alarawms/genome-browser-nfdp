SPECIES_META = {
    "sheep": {
        "assembly_name": "Oar_rambouillet_v1.0",
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


def make_assembly_config(species_id: str, base_url: str) -> dict:
    meta = SPECIES_META[species_id]
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


def make_track_configs(species_id: str, base_url: str) -> list[dict]:
    meta = SPECIES_META[species_id]
    ann_url = f"{base_url}/annotations/{species_id}"
    qtl_url = f"{base_url}/qtl/{species_id}"
    assembly_name = meta["assembly_name"]
    return [
        {
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
        },
        {
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
        },
    ]
