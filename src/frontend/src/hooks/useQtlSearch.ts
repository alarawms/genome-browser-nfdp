import { useEffect, useRef, useState } from "react";
import { api, QTL, Trait } from "../api/client";

interface Filters {
  chromosome?: string;
  traitCategory?: string;
}

export function useQtlSearch(speciesId: string) {
  const [qtls, setQtls] = useState<QTL[]>([]);
  const [traits, setTraits] = useState<Trait[]>([]);
  const [filters, setFilters] = useState<Filters>({});
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // Fetch traits when species changes
  useEffect(() => {
    api.getTraits(speciesId).then(setTraits);
  }, [speciesId]);

  // Fetch QTLs when species or filters change (debounced)
  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      const params: Record<string, string> = {};
      if (filters.chromosome) params.chromosome = filters.chromosome;
      if (filters.traitCategory) params.trait_category = filters.traitCategory;
      api.getQtls(speciesId, params).then((data) => {
        setQtls(data);
        setLoading(false);
      });
    }, 200);
    return () => clearTimeout(debounceRef.current);
  }, [speciesId, filters]);

  return { qtls, traits, filters, setFilters, loading };
}
