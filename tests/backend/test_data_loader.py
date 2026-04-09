import os
import pytest
from src.backend.data_loader import DataStore

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


@pytest.fixture
def store():
    return DataStore(data_dir=FIXTURES_DIR)


def test_load_species_qtls(store):
    sheep_qtls = store.get_qtls("sheep")
    assert len(sheep_qtls) == 3
    assert sheep_qtls[0]["trait"] == "Milk yield"


def test_get_qtls_filtered_by_chromosome(store):
    qtls = store.get_qtls("sheep", chromosome="1")
    assert len(qtls) == 2
    assert all(q["chromosome"] == "1" for q in qtls)


def test_get_qtls_filtered_by_trait_category(store):
    qtls = store.get_qtls("sheep", trait_category="Milk")
    assert len(qtls) == 1
    assert qtls[0]["trait"] == "Milk yield"


def test_get_qtls_filtered_by_region(store):
    qtls = store.get_qtls("sheep", chromosome="1", start=50000000, end=55000000)
    assert len(qtls) == 1
    assert qtls[0]["trait"] == "Body weight"


def test_get_traits(store):
    traits = store.get_traits("sheep")
    categories = {t["category"] for t in traits}
    assert "Milk" in categories
    assert "Growth" in categories
    assert "Wool" in categories


def test_search(store):
    results = store.search("milk")
    assert len(results) >= 1
    assert any("Milk" in r["label"] for r in results)


def test_search_with_species_filter(store):
    results = store.search("milk", species_id="goat")
    assert all(r["species_id"] == "goat" for r in results)


def test_unknown_species_returns_empty(store):
    qtls = store.get_qtls("unknown")
    assert qtls == []
