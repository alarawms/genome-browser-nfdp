from src.backend.jbrowse_config import make_assembly_config, make_track_configs

BASE_URL = "http://localhost:8000/data"


def test_sheep_assembly_config():
    config = make_assembly_config("sheep", BASE_URL)
    assert config["name"] == "Oar_rambouillet_v1.0"
    assert "sequence" in config
    adapter = config["sequence"]["adapter"]
    assert adapter["type"] == "BgzipFastaAdapter"
    assert "sheep" in adapter["fastaLocation"]["uri"]


def test_goat_assembly_config():
    config = make_assembly_config("goat", BASE_URL)
    assert config["name"] == "CHIR_1.0"


def test_unknown_species_raises():
    import pytest

    with pytest.raises(KeyError):
        make_assembly_config("unknown", BASE_URL)


def test_track_configs():
    tracks = make_track_configs("sheep", BASE_URL)
    track_names = [t["name"] for t in tracks]
    assert "Gene Annotations" in track_names
    assert "QTLs" in track_names


def test_track_adapters():
    tracks = make_track_configs("sheep", BASE_URL)
    gene_track = next(t for t in tracks if t["name"] == "Gene Annotations")
    assert gene_track["adapter"]["type"] == "Gff3TabixAdapter"
    qtl_track = next(t for t in tracks if t["name"] == "QTLs")
    assert qtl_track["adapter"]["type"] == "BedTabixAdapter"
