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
    # Trait identity
    trait: str
    trait_category: str
    trait_variant: str | None = None   # more specific than trait (e.g. "body weight at 80 days")
    base_trait: str | None = None
    # Study context
    breed: str | None = None           # breed the QTL was discovered in
    flank_marker: str | None = None    # e.g. rsID of the lead SNP
    p_value: str | None = None         # string (keeps precision)
    variance: str | None = None        # % variance explained
    score: float | None = None         # GFF col 6 value (often null for QTLdb)
    pubmed_id: str | None = None
    # QTLdb canonical IDs
    qtldb_id: str | None = None
    qtldb_trait_id: str | None = None
    # Gene (when QTLdb mapped the QTL to a specific gene)
    gene_ncbi_id: str | None = None
    # Ontology enrichments (names from QTLdb; IDs + IRIs from EBI OLS)
    vto_name: str | None = None        # Vertebrate Trait Ontology label
    vto_id: str | None = None          # e.g. "VT:0001259"
    vto_iri: str | None = None
    cmo_name: str | None = None        # Clinical Measurement Ontology label
    cmo_id: str | None = None          # e.g. "CMO:0000012"
    cmo_iri: str | None = None
    pto_name: str | None = None        # Livestock Product Trait (not on OLS4 — name only)
    pto_id: str | None = None
    pto_iri: str | None = None
    # Genes overlapping this QTL (populated by scripts/map_qtl_genes.py against
    # the gene-annotation track). Capped at MAX_GENES_PER_QTL = 200 entries.
    overlapping_genes: list[dict] | None = None
    overlapping_gene_count: int | None = None
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
