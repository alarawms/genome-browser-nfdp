import { useEffect, useMemo, useState } from "react";
import { api, AnnotationTrackSummary, AnnotationPair } from "../api/client";

interface Props {
  speciesId: string;
}

function fmt(n: number | undefined): string {
  if (n == null) return "—";
  return n.toLocaleString();
}

function jaccardColor(j: number): string {
  // Heatmap: red (low agreement) → amber → green (high)
  if (j >= 0.7) return "bg-emerald-700/70 text-emerald-50";
  if (j >= 0.5) return "bg-emerald-900/60 text-emerald-200";
  if (j >= 0.3) return "bg-amber-900/60 text-amber-200";
  return "bg-red-900/60 text-red-200";
}

export default function AnnotationComparison({ speciesId }: Props) {
  const [tracks, setTracks] = useState<AnnotationTrackSummary[]>([]);
  const [pairs, setPairs] = useState<Record<string, AnnotationPair>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      api.getAnnotationsSummary(speciesId).catch(() => null),
      api.getAnnotationsCompare(speciesId).catch(() => null),
    ]).then(([summary, compare]) => {
      if (cancelled) return;
      if (!summary || !compare) {
        setError("No annotation comparison data — run scripts/compare_annotations.py first.");
      } else {
        setTracks(summary.tracks);
        setPairs(compare.pairs);
      }
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [speciesId]);

  const trackIds = useMemo(() => tracks.map((t) => t.track_id), [tracks]);

  // Build a [trackA][trackB] -> AnnotationPair lookup, normalized order
  const pairLookup = useMemo(() => {
    const lk: Record<string, Record<string, AnnotationPair>> = {};
    for (const p of Object.values(pairs)) {
      (lk[p.a] = lk[p.a] || {})[p.b] = p;
      (lk[p.b] = lk[p.b] || {})[p.a] = p;
    }
    return lk;
  }, [pairs]);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="border-b border-gray-800 bg-gray-950 px-4 py-1.5 text-left text-xs text-gray-400 hover:bg-gray-900"
      >
        ▸ Annotation comparison ({tracks.length} tracks
        {Object.keys(pairs).length > 0 && `, ${Object.keys(pairs).length} pairs`})
      </button>
    );
  }

  return (
    <div className="border-b border-gray-800 bg-gray-950 px-4 py-3">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-bold text-emerald-400">
          Annotation comparison
        </h2>
        <button
          onClick={() => setOpen(false)}
          className="text-xs text-gray-500 hover:text-gray-300"
        >
          ▾ collapse
        </button>
      </div>

      {loading && <p className="text-xs text-gray-500">loading…</p>}
      {error && <p className="text-xs text-red-400">{error}</p>}

      {!loading && !error && tracks.length > 0 && (
        <>
          {/* Per-track summary cards */}
          <div className="mb-3 grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
            {tracks.map((t) => (
              <div
                key={t.track_id}
                className="rounded border border-gray-800 bg-gray-900 p-2"
              >
                <p className="font-mono text-[11px] uppercase tracking-wide text-emerald-400">
                  {t.track_id}
                </p>
                <p className="mt-0.5 text-xs text-gray-300">{t.label}</p>
                <div className="mt-1 grid grid-cols-2 gap-x-2 gap-y-0.5 text-[11px] text-gray-400">
                  <span>
                    <span className="text-gray-500">Genes: </span>
                    <span className="font-mono text-gray-200">{fmt(t.gene_count)}</span>
                  </span>
                  <span>
                    <span className="text-gray-500">Named: </span>
                    <span className="font-mono text-gray-200">
                      {t.named_pct != null ? `${t.named_pct}%` : "—"}
                    </span>
                  </span>
                  <span>
                    <span className="text-gray-500">Mean len: </span>
                    <span className="font-mono text-gray-200">
                      {t.mean_length_bp ? `${(t.mean_length_bp / 1000).toFixed(1)} kb` : "—"}
                    </span>
                  </span>
                  <span>
                    <span className="text-gray-500">Chroms: </span>
                    <span className="font-mono text-gray-200">{fmt(t.chromosome_count)}</span>
                  </span>
                </div>
                {t.biotype_mix && Object.keys(t.biotype_mix).length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-0.5 text-[9px]">
                    {Object.entries(t.biotype_mix)
                      .slice(0, 4)
                      .map(([bt, n]) => (
                        <span
                          key={bt}
                          className="rounded bg-gray-800 px-1 py-0.5 font-mono text-gray-400"
                          title={`${n} ${bt}`}
                        >
                          {bt}: {n}
                        </span>
                      ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pairwise concordance heatmap */}
          {trackIds.length > 1 && (
            <div>
              <p className="mb-1 text-[10px] uppercase tracking-wide text-gray-500">
                Pairwise concordance — gene Jaccard at ≥50% reciprocal overlap
              </p>
              <div className="overflow-x-auto">
                <table className="text-[11px]">
                  <thead>
                    <tr>
                      <th className="px-2 py-1 text-left text-gray-500"></th>
                      {trackIds.map((tid) => (
                        <th
                          key={tid}
                          className="px-2 py-1 text-center font-mono text-gray-400"
                        >
                          {tid}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {trackIds.map((row) => (
                      <tr key={row}>
                        <th className="px-2 py-1 text-right font-mono text-gray-400">
                          {row}
                        </th>
                        {trackIds.map((col) => {
                          if (row === col) {
                            return (
                              <td
                                key={col}
                                className="border border-gray-800 px-2 py-1 text-center text-gray-700"
                              >
                                —
                              </td>
                            );
                          }
                          const p = pairLookup[row]?.[col];
                          if (!p) {
                            return (
                              <td
                                key={col}
                                className="border border-gray-800 px-2 py-1 text-center text-gray-700"
                              >
                                ?
                              </td>
                            );
                          }
                          const tip =
                            `Jaccard ${(p.gene_jaccard).toFixed(3)} · ` +
                            `matched ${p.matched_pairs.toLocaleString()} · ` +
                            `unique-${p.a==row?'a':'b'} ${(p.a===row?p.unique_a_count:p.unique_b_count).toLocaleString()} · ` +
                            `unique-${p.a===row?'b':'a'} ${(p.a===row?p.unique_b_count:p.unique_a_count).toLocaleString()} · ` +
                            `name agreement ${p.name_agreement_pct}% · ` +
                            `position drift median ${p.median_position_drift_bp.toLocaleString()} bp`;
                          return (
                            <td
                              key={col}
                              className={`border border-gray-800 px-2 py-1 text-center font-mono ${jaccardColor(p.gene_jaccard)}`}
                              title={tip}
                            >
                              {p.gene_jaccard.toFixed(2)}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-1 text-[10px] text-gray-600">
                Hover a cell for matched-pair counts, name agreement, median position drift.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
