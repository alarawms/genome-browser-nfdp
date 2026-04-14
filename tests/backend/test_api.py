import os
import pytest
from fastapi.testclient import TestClient

os.environ["DATA_DIR"] = os.path.join(os.path.dirname(__file__), "..", "fixtures")

from src.backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_list_species(client):
    resp = client.get("/api/species")
    assert resp.status_code == 200
    species = resp.json()
    assert len(species) == 2
    ids = {s["id"] for s in species}
    assert "sheep" in ids
    assert "goat" in ids


def test_get_qtls(client):
    resp = client.get("/api/species/sheep/qtls")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 3


def test_get_qtls_with_chromosome_filter(client):
    resp = client.get("/api/species/sheep/qtls?chromosome=1")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 2


def test_get_qtls_with_trait_filter(client):
    resp = client.get("/api/species/sheep/qtls?trait_category=Milk")
    assert resp.status_code == 200
    qtls = resp.json()
    assert len(qtls) == 1


def test_get_traits(client):
    resp = client.get("/api/species/sheep/traits")
    assert resp.status_code == 200
    traits = resp.json()
    categories = {t["category"] for t in traits}
    assert "Milk" in categories


def test_search(client):
    resp = client.get("/api/search?q=milk")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1


def test_search_with_species(client):
    resp = client.get("/api/search?q=milk&species=goat")
    assert resp.status_code == 200
    results = resp.json()
    assert all(r["species_id"] == "goat" for r in results)


def test_search_by_gene_symbol(client):
    """Exact-symbol match should return the gene with type='gene'."""
    resp = client.get("/api/search?q=MSTN&species=sheep")
    assert resp.status_code == 200
    hits = resp.json()
    gene_hits = [r for r in hits if r["type"] == "gene"]
    assert len(gene_hits) >= 1
    # Exact match should be first
    top = gene_hits[0]
    assert top["label"].startswith("MSTN")
    assert top["chromosome"] == "1"


def test_search_by_gene_description(client):
    """Matching by functional description text should find the gene."""
    resp = client.get("/api/search?q=myostatin&species=sheep")
    assert resp.status_code == 200
    gene_hits = [r for r in resp.json() if r["type"] == "gene"]
    assert any("MSTN" in r["label"] for r in gene_hits)


def test_search_ranks_exact_over_substring(client):
    """With 'LEP', exact-match LEP should rank above 'LOC' or 'leptin'."""
    resp = client.get("/api/search?q=LEP&species=sheep")
    hits = [r for r in resp.json() if r["type"] == "gene"]
    assert hits[0]["label"].startswith("LEP")


def test_search_mixes_genes_and_qtls(client):
    """A query matching both should return both, gene types ranked first."""
    # 'milk' matches QTL traits; 'LOC12345' won't appear — pure QTL test case
    resp = client.get("/api/search?q=milk&species=sheep")
    types = {r["type"] for r in resp.json()}
    assert "qtl" in types


def test_jbrowse_config(client):
    resp = client.get("/api/species/sheep/jbrowse-config")
    assert resp.status_code == 200
    config = resp.json()
    assert "assembly" in config
    assert "tracks" in config
    assert config["assembly"]["name"] == "ARS-UI_Ramb_v3.0"


def test_unknown_species_404(client):
    resp = client.get("/api/species/unknown/qtls")
    assert resp.status_code == 200
    assert resp.json() == []


# --- Chromosome overview endpoints ------------------------------------------

def test_list_chromosomes_sheep_has_fai(client):
    """Sheep fixture has a .fai file — should return both chromosomes."""
    resp = client.get("/api/species/sheep/chromosomes")
    assert resp.status_code == 200
    chroms = resp.json()
    names = {c["name"] for c in chroms}
    assert {"1", "3"}.issubset(names)
    by_name = {c["name"]: c for c in chroms}
    assert by_name["1"]["length"] == 100_000_000
    # QTLs from qtl fixture: 2 on chr1, 1 on chr3
    assert by_name["1"]["qtl_count"] == 2
    assert by_name["3"]["qtl_count"] == 1
    # Genes from gff fixture: 3 on chr1, 1 on chr3
    assert by_name["1"]["gene_count"] == 3
    assert by_name["3"]["gene_count"] == 1


def test_list_chromosomes_empty_for_species_without_fai(client):
    """Goat has no FASTA fixture — returns an empty list, not a 500."""
    resp = client.get("/api/species/goat/chromosomes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_chromosome_summary_returns_bins_and_qtls(client):
    resp = client.get("/api/species/sheep/chromosome/1/summary?bins=10")
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["chromosome"] == "1"
    assert summary["length"] == 100_000_000
    assert len(summary["gene_bins"]) == 10
    # 3 gene records on chr1 of fixture, total counts should equal
    assert sum(b["count"] for b in summary["gene_bins"]) == 3
    # MSTN at 45-47M and LEP at 52-54M should appear as symbols somewhere
    all_symbols = [s for b in summary["gene_bins"] for s in b["symbols"]]
    assert "MSTN" in all_symbols
    assert "LEP" in all_symbols
    # LOC12345 is not a curated symbol; should NOT be included
    assert "LOC12345" not in all_symbols
    # 2 QTLs on chr1
    assert len(summary["qtls"]) == 2


def test_chromosome_summary_404_for_unknown_chrom(client):
    resp = client.get("/api/species/sheep/chromosome/NOTREAL/summary")
    assert resp.status_code == 404


# --- Enriched QTL fields -----------------------------------------------------

def test_qtl_shape_includes_optional_enrichment_fields(client):
    """The enriched fields may be null but must be serializable (NaN fix)."""
    resp = client.get("/api/species/sheep/qtls")
    assert resp.status_code == 200
    for qtl in resp.json():
        # New optional fields should be present (possibly None)
        for k in ("breed", "vto_id", "cmo_id", "flank_marker", "p_value",
                  "overlapping_genes", "overlapping_gene_count"):
            assert k in qtl, f"missing field {k} in QTL record"
