from src.backend.models import Species, QTL, Trait, SearchResult


def test_species_model():
    s = Species(
        id="sheep",
        name="Sheep",
        scientific_name="Ovis aries",
        assembly="Oar_rambouillet_v1.0",
        chromosome_count=27,
    )
    assert s.id == "sheep"
    assert s.chromosome_count == 27


def test_qtl_model():
    q = QTL(
        id="qtl_001",
        species_id="sheep",
        chromosome="1",
        start=45230100,
        end=47891200,
        trait="Milk yield",
        trait_category="Milk",
        score=4.2,
        pubmed_id="28374882",
        source="Animal QTLdb",
    )
    assert q.chromosome == "1"
    assert q.score == 4.2


def test_trait_model():
    t = Trait(name="Milk yield", category="Milk", qtl_count=47)
    assert t.qtl_count == 47


def test_search_result():
    r = SearchResult(
        type="qtl",
        species_id="sheep",
        label="Milk yield QTL",
        chromosome="1",
        start=45230100,
        end=47891200,
    )
    assert r.type == "qtl"
