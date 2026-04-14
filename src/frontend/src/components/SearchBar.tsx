import { useRef, useState } from "react";
import { api, SearchResult } from "../api/client";

interface Props {
  speciesId: string;
  onNavigate: (chr: string, start: number, end: number) => void;
}

export default function SearchBar({ speciesId, onNavigate }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  function handleChange(value: string) {
    setQuery(value);
    clearTimeout(debounceRef.current);
    if (value.length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }
    debounceRef.current = setTimeout(() => {
      api.search(value, speciesId).then((r) => {
        setResults(r.slice(0, 10));
        setOpen(true);
      });
    }, 300);
  }

  function handleSelect(r: SearchResult) {
    onNavigate(r.chromosome, r.start, r.end);
    setOpen(false);
    setQuery("");
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 200)}
        placeholder="Search genes, QTLs, traits..."
        className="w-56 rounded-lg border border-gray-600 bg-gray-800 px-3 py-1.5 text-sm text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
      />
      {open && results.length > 0 && (
        <div className="absolute right-0 top-full z-50 mt-1 max-h-96 w-96 overflow-y-auto rounded-lg border border-gray-700 bg-gray-800 shadow-xl">
          {results.map((r, i) => {
            const isGene = r.type === "gene";
            const tagColor = isGene
              ? "bg-emerald-900/60 text-emerald-300"
              : "bg-amber-900/60 text-amber-300";
            return (
              <button
                key={i}
                onMouseDown={() => handleSelect(r)}
                className="flex w-full flex-col px-3 py-2 text-left hover:bg-gray-700"
              >
                <div className="flex items-center gap-2">
                  <span className={`rounded px-1.5 py-0.5 text-[9px] font-mono uppercase ${tagColor}`}>
                    {isGene ? "GENE" : "QTL"}
                  </span>
                  <span className="truncate text-sm text-white">{r.label}</span>
                </div>
                <span className="mt-0.5 font-mono text-xs text-gray-400">
                  {r.chromosome}:{r.start.toLocaleString()}-
                  {r.end.toLocaleString()} · {r.species_id}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
