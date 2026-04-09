import { useCallback, useEffect, useState } from "react";
import { api, Species } from "../api/client";

export function useSpecies() {
  const [species, setSpecies] = useState<Species[]>([]);
  const [selectedId, setSelectedId] = useState<string>("sheep");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSpecies().then((data) => {
      setSpecies(data);
      setLoading(false);
    });
  }, []);

  const selected = species.find((s) => s.id === selectedId) ?? null;

  const select = useCallback((id: string) => setSelectedId(id), []);

  return { species, selected, selectedId, select, loading };
}
