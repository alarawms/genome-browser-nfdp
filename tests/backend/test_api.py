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


def test_jbrowse_config(client):
    resp = client.get("/api/species/sheep/jbrowse-config")
    assert resp.status_code == 200
    config = resp.json()
    assert "assembly" in config
    assert "tracks" in config
    assert config["assembly"]["name"] == "ARS-UI_Ramb_v2.0"


def test_unknown_species_404(client):
    resp = client.get("/api/species/unknown/qtls")
    assert resp.status_code == 200
    assert resp.json() == []
