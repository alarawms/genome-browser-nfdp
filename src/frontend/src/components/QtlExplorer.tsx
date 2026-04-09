import { useQtlSearch } from "../hooks/useQtlSearch";
import QtlDetail from "./QtlDetail";

interface Props {
  speciesId: string;
  onQtlClick: (chr: string, start: number, end: number) => void;
}

const CHROMOSOMES = [
  ...Array.from({ length: 26 }, (_, i) => String(i + 1)),
  "X",
];

export default function QtlExplorer({ speciesId, onQtlClick }: Props) {
  const { qtls, traits, filters, setFilters, loading } =
    useQtlSearch(speciesId);

  return (
    <div className="flex flex-col gap-4 p-4">
      <h2 className="text-sm font-bold text-amber-400">QTL Explorer</h2>

      {/* Chromosome picker */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">Chromosome</p>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setFilters((f) => ({ ...f, chromosome: undefined }))}
            className={`rounded px-2 py-0.5 text-xs ${
              !filters.chromosome
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-white"
            }`}
          >
            All
          </button>
          {CHROMOSOMES.map((chr) => (
            <button
              key={chr}
              onClick={() => setFilters((f) => ({ ...f, chromosome: chr }))}
              className={`rounded px-2 py-0.5 text-xs ${
                filters.chromosome === chr
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:text-white"
              }`}
            >
              {chr}
            </button>
          ))}
        </div>
      </div>

      {/* Trait category filter */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">Trait Category</p>
        <div className="flex flex-col gap-1">
          <button
            onClick={() =>
              setFilters((f) => ({ ...f, traitCategory: undefined }))
            }
            className={`text-left text-xs ${
              !filters.traitCategory ? "text-emerald-400" : "text-gray-400"
            }`}
          >
            {!filters.traitCategory ? "☑" : "☐"} All categories
          </button>
          {traits.map((t) => (
            <button
              key={t.category}
              onClick={() =>
                setFilters((f) => ({
                  ...f,
                  traitCategory:
                    f.traitCategory === t.category ? undefined : t.category,
                }))
              }
              className={`text-left text-xs ${
                filters.traitCategory === t.category
                  ? "text-emerald-400"
                  : "text-gray-400"
              }`}
            >
              {filters.traitCategory === t.category ? "☑" : "☐"} {t.category} (
              {t.qtl_count})
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div>
        <p className="mb-2 text-xs uppercase text-gray-500">
          Results ({loading ? "..." : qtls.length} QTLs)
        </p>
        <div className="flex flex-col gap-2">
          {qtls.map((qtl) => (
            <QtlDetail key={qtl.id} qtl={qtl} onNavigate={onQtlClick} />
          ))}
          {!loading && qtls.length === 0 && (
            <p className="text-xs text-gray-500">No QTLs match filters</p>
          )}
        </div>
      </div>
    </div>
  );
}
