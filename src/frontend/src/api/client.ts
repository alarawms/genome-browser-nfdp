const BASE = "";

export interface Species {
  id: string;
  name: string;
  scientific_name: string;
  assembly: string;
  chromosome_count: number;
}

export interface QTL {
  id: string;
  species_id: string;
  chromosome: string;
  start: number;
  end: number;
  // Trait identity
  trait: string;
  trait_category: string;
  trait_variant?: string | null;
  base_trait?: string | null;
  // Study context
  breed?: string | null;
  flank_marker?: string | null;       // rsID
  p_value?: string | null;
  variance?: string | null;
  score: number | null;
  pubmed_id: string | null;
  // QTLdb canonical IDs
  qtldb_id?: string | null;
  qtldb_trait_id?: string | null;
  // Gene linkout
  gene_ncbi_id?: string | null;
  // Ontology enrichments
  vto_name?: string | null;
  vto_id?: string | null;
  vto_iri?: string | null;
  cmo_name?: string | null;
  cmo_id?: string | null;
  cmo_iri?: string | null;
  pto_name?: string | null;
  pto_id?: string | null;
  pto_iri?: string | null;
  // Genes whose interval overlaps this QTL (from liftoff gene annotation)
  overlapping_genes?: GeneOverlap[] | null;
  overlapping_gene_count?: number | null;
  source: string | null;
}

export interface GeneOverlap {
  id: string;             // Hu locus_tag (e.g. "R6Z07_001521")
  name: string;           // fallback display label
  biotype?: string | null;
  start: number;
  end: number;
  // Rambouillet cross-reference (populated when paftools-lifted Ramb gene
  // overlaps the Hu gene at ≥30% coverage)
  symbol?: string | null;              // e.g. "MSTN", "LEP"
  description?: string | null;         // e.g. "myostatin"
  ncbi_gene_id?: string | null;        // links to ncbi.nlm.nih.gov/gene/<id>
  rambouillet_biotype?: string | null;
  ramb_overlap_frac?: number | null;   // 0..1
}

export interface Trait {
  name: string;
  category: string;
  qtl_count: number;
}

export interface SearchResult {
  type: string;
  species_id: string;
  label: string;
  chromosome: string;
  start: number;
  end: number;
}

export interface JBrowseConfig {
  assembly: Record<string, unknown>;
  tracks: Record<string, unknown>[];
}

export interface ChromosomeInfo {
  name: string;
  length: number;
  gene_count: number;
  qtl_count: number;
}

export interface GeneBin {
  start: number;
  end: number;
  count: number;
  symbols: string[];
}

export interface ChromosomeQtl {
  id: string;
  start: number;
  end: number;
  trait: string;
  trait_category: string;
  breed?: string | null;
  overlapping_gene_count: number;
}

export interface ChromosomeSummary {
  chromosome: string;
  length: number;
  bin_size: number;
  gene_bins: GeneBin[];
  qtls: ChromosomeQtl[];
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getSpecies: () => fetchJson<Species[]>("/api/species"),

  getQtls: (speciesId: string, params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return fetchJson<QTL[]>(`/api/species/${speciesId}/qtls${qs}`);
  },

  getTraits: (speciesId: string) =>
    fetchJson<Trait[]>(`/api/species/${speciesId}/traits`),

  search: (query: string, species?: string) => {
    const params = new URLSearchParams({ q: query });
    if (species) params.set("species", species);
    return fetchJson<SearchResult[]>(`/api/search?${params}`);
  },

  getJBrowseConfig: (speciesId: string) =>
    fetchJson<JBrowseConfig>(`/api/species/${speciesId}/jbrowse-config`),

  getChromosomes: (speciesId: string) =>
    fetchJson<ChromosomeInfo[]>(`/api/species/${speciesId}/chromosomes`),

  getChromosomeSummary: (speciesId: string, chrom: string, bins = 200) =>
    fetchJson<ChromosomeSummary>(
      `/api/species/${speciesId}/chromosome/${encodeURIComponent(chrom)}/summary?bins=${bins}`
    ),
};
