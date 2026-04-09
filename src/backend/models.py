from pydantic import BaseModel


class Species(BaseModel):
    id: str
    name: str
    scientific_name: str
    assembly: str
    chromosome_count: int


class QTL(BaseModel):
    id: str
    species_id: str
    chromosome: str
    start: int
    end: int
    trait: str
    trait_category: str
    score: float | None = None
    pubmed_id: str | None = None
    source: str | None = None


class Trait(BaseModel):
    name: str
    category: str
    qtl_count: int


class SearchResult(BaseModel):
    type: str  # "qtl" or "gene"
    species_id: str
    label: str
    chromosome: str
    start: int
    end: int
