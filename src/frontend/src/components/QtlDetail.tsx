import { QTL } from "../api/client";

interface Props {
  qtl: QTL;
  onNavigate: (chr: string, start: number, end: number) => void;
}

const stop = (e: React.MouseEvent) => e.stopPropagation();

export default function QtlDetail({ qtl, onNavigate }: Props) {
  const variantDistinct =
    qtl.trait_variant && qtl.trait_variant.toLowerCase() !== qtl.trait.toLowerCase();

  return (
    <button
      onClick={() => onNavigate(qtl.chromosome, qtl.start, qtl.end)}
      className="w-full rounded-md bg-gray-800 p-3 text-left transition-colors hover:bg-gray-750 border-l-[3px]"
      style={{ borderLeftColor: categoryColor(qtl.trait_category) }}
    >
      {/* Headline: trait + (more specific) variant */}
      <p className="text-sm font-semibold text-white">{qtl.trait}</p>
      {variantDistinct && (
        <p className="mt-0.5 text-[11px] italic text-gray-500">
          {qtl.trait_variant}
        </p>
      )}

      {/* Coordinates (monospace; chromosome shown raw to match assembly naming) */}
      <p className="mt-1 font-mono text-xs text-gray-400">
        {qtl.chromosome}:{qtl.start.toLocaleString()}-{qtl.end.toLocaleString()}
      </p>

      {/* Breed chip */}
      {qtl.breed && (
        <div className="mt-1.5">
          <span
            className="inline-block rounded bg-amber-900/40 px-1.5 py-0.5 text-[10px] text-amber-300"
            title="Breed in which this QTL was originally characterized"
          >
            {qtl.breed}
          </span>
        </div>
      )}

      {/* Ontology badges (linkouts to EBI OLS4) */}
      {(qtl.vto_id || qtl.cmo_id || qtl.pto_name) && (
        <div className="mt-1.5 flex flex-wrap gap-1">
          {qtl.vto_id && qtl.vto_iri && (
            <a
              href={`https://www.ebi.ac.uk/ols4/ontologies/vt/classes?iri=${encodeURIComponent(qtl.vto_iri)}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={stop}
              className="inline-flex items-center gap-1 rounded bg-blue-900/50 px-1.5 py-0.5 text-[10px] text-blue-300 hover:bg-blue-900/70"
              title={`Vertebrate Trait Ontology · ${qtl.vto_id}`}
            >
              <span className="font-mono text-blue-400">VT</span>
              <span>{qtl.vto_name}</span>
              <span className="text-blue-500">↗</span>
            </a>
          )}
          {qtl.cmo_id && qtl.cmo_iri && (
            <a
              href={`https://www.ebi.ac.uk/ols4/ontologies/cmo/classes?iri=${encodeURIComponent(qtl.cmo_iri)}`}
              target="_blank"
              rel="noopener noreferrer"
              onClick={stop}
              className="inline-flex items-center gap-1 rounded bg-purple-900/50 px-1.5 py-0.5 text-[10px] text-purple-300 hover:bg-purple-900/70"
              title={`Clinical Measurement Ontology · ${qtl.cmo_id}`}
            >
              <span className="font-mono text-purple-400">CMO</span>
              <span>{qtl.cmo_name}</span>
              <span className="text-purple-500">↗</span>
            </a>
          )}
          {qtl.pto_name && !qtl.pto_id && (
            <span
              className="inline-flex items-center gap-1 rounded bg-gray-700/50 px-1.5 py-0.5 text-[10px] text-gray-400"
              title="Livestock Product Trait — not on EBI OLS, name only"
            >
              <span className="font-mono text-gray-500">LPT</span>
              <span>{qtl.pto_name}</span>
            </span>
          )}
        </div>
      )}

      {/* Overlapping genes — per-track sections if multi-annotation, else single list */}
      {(() => {
        const byTrack = qtl.overlapping_genes_by_track;
        const trackEntries = byTrack
          ? Object.entries(byTrack).filter(([, gs]) => gs && gs.length > 0)
          : [];
        const hasMultiTrack = trackEntries.length > 1;
        const legacy = qtl.overlapping_genes;

        const renderChips = (genes: typeof qtl.overlapping_genes, max = 6) => (
          <div className="flex flex-wrap gap-1">
            {(genes || []).slice(0, max).map((g, i) => {
              const hasSymbol = !!g.symbol && !g.symbol.startsWith("LOC");
              const label = hasSymbol ? g.symbol : g.name;
              const tooltipParts = [
                hasSymbol ? `${g.symbol}${g.name !== g.symbol ? ` (${g.name})` : ""}` : g.name,
                g.description,
                g.biotype,
                `${g.start.toLocaleString()}-${g.end.toLocaleString()}`,
              ].filter(Boolean);
              return (
                <span key={`${g.id}-${i}`} className="inline-flex rounded overflow-hidden">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onNavigate(qtl.chromosome, g.start, g.end);
                    }}
                    className={`px-1.5 py-0.5 text-[10px] ${
                      hasSymbol
                        ? "bg-emerald-700/50 text-emerald-100 hover:bg-emerald-700/80 font-sans"
                        : "bg-emerald-900/40 text-emerald-300 hover:bg-emerald-900/70 font-mono"
                    }`}
                    title={tooltipParts.join(" · ")}
                  >
                    {label}
                  </button>
                  {g.ncbi_gene_id && (
                    <a
                      href={`https://www.ncbi.nlm.nih.gov/gene/${g.ncbi_gene_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={stop}
                      className="px-1 py-0.5 text-[10px] bg-emerald-900/60 text-emerald-400 hover:bg-emerald-900/90 border-l border-emerald-950"
                      title={`NCBI Gene ${g.ncbi_gene_id}`}
                    >
                      ↗
                    </a>
                  )}
                </span>
              );
            })}
            {(genes?.length ?? 0) > max && (
              <span
                className="inline-block rounded bg-gray-700/50 px-1.5 py-0.5 text-[10px] text-gray-400"
                title={(genes || []).slice(max).map((g) => g.symbol || g.name).join(", ")}
              >
                +{(genes?.length ?? 0) - max} more
              </span>
            )}
          </div>
        );

        if (hasMultiTrack) {
          return (
            <div className="mt-1.5">
              <p className="mb-1 text-[10px] uppercase tracking-wide text-gray-500">
                Overlapping genes per annotation
              </p>
              <div className="flex flex-col gap-1.5">
                {trackEntries.map(([trackId, genes]) => (
                  <div key={trackId} className="border-l-2 border-gray-700 pl-2">
                    <p className="mb-0.5 font-mono text-[9px] uppercase tracking-wide text-gray-500">
                      {trackId} ({genes.length})
                    </p>
                    {renderChips(genes, 5)}
                  </div>
                ))}
              </div>
            </div>
          );
        }
        if (legacy && legacy.length > 0) {
          return (
            <div className="mt-1.5">
              <p className="mb-0.5 text-[10px] uppercase tracking-wide text-gray-500">
                Overlapping genes ({qtl.overlapping_gene_count})
              </p>
              {renderChips(legacy, 8)}
            </div>
          );
        }
        return null;
      })()}

      {/* Stats row: rsID, P-value, gene, PMID */}
      <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px]">
        {qtl.flank_marker && qtl.flank_marker.startsWith("rs") && (
          <a
            href={`https://www.ncbi.nlm.nih.gov/snp/${qtl.flank_marker}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={stop}
            className="font-mono text-cyan-400 hover:underline"
            title="Lead SNP (dbSNP)"
          >
            {qtl.flank_marker}↗
          </a>
        )}
        {qtl.p_value && (
          <span className="text-gray-400" title="P-value as reported by study">
            <span className="text-gray-500">P=</span>
            {qtl.p_value}
          </span>
        )}
        {qtl.gene_ncbi_id && (
          <a
            href={`https://www.ncbi.nlm.nih.gov/gene/${qtl.gene_ncbi_id}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={stop}
            className="text-emerald-400 hover:underline"
            title="NCBI Gene"
          >
            Gene:{qtl.gene_ncbi_id}↗
          </a>
        )}
        {qtl.pubmed_id && (
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${qtl.pubmed_id}/`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={stop}
            className="text-blue-400 hover:underline"
            title="PubMed"
          >
            PMID:{qtl.pubmed_id}↗
          </a>
        )}
        {qtl.score != null && qtl.score !== 0 && (
          <span style={{ color: categoryColor(qtl.trait_category) }}>
            Score: {qtl.score}
          </span>
        )}
      </div>
    </button>
  );
}

function categoryColor(category: string): string {
  const colors: Record<string, string> = {
    Milk: "#4ade80",
    Meat: "#f87171",
    "Wool/Fiber": "#c084fc",
    "Disease Resistance": "#38bdf8",
    Reproduction: "#fb923c",
    Growth: "#facc15",
    Morphology: "#a78bfa",
    Other: "#94a3b8",
  };
  return colors[category] ?? colors.Other;
}
