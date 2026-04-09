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
  trait: string;
  trait_category: string;
  score: number | null;
  pubmed_id: string | null;
  source: string | null;
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
};
