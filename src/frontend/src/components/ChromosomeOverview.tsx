import { useEffect, useMemo, useRef, useState } from "react";
import { api, ChromosomeInfo, ChromosomeSummary } from "../api/client";

interface Props {
  speciesId: string;
  onNavigate: (chrom: string, start: number, end: number) => void;
}

// Match QtlDetail's category palette for consistency
const CATEGORY_COLOR: Record<string, string> = {
  Milk: "#4ade80",
  Meat: "#f87171",
  "Wool/Fiber": "#c084fc",
  "Disease Resistance": "#38bdf8",
  Reproduction: "#fb923c",
  Growth: "#facc15",
  Morphology: "#a78bfa",
  Other: "#94a3b8",
};

function humanBases(n: number): string {
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)} Gb`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)} Mb`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)} Kb`;
  return `${n} bp`;
}

export default function ChromosomeOverview({ speciesId, onNavigate }: Props) {
  const [chromosomes, setChromosomes] = useState<ChromosomeInfo[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [summary, setSummary] = useState<ChromosomeSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [hover, setHover] = useState<{
    x: number;
    y: number;
    text: string;
  } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [width, setWidth] = useState(900);

  // Load chromosome list when species changes
  useEffect(() => {
    let cancelled = false;
    api.getChromosomes(speciesId).then((list) => {
      if (cancelled) return;
      setChromosomes(list);
      // Pre-select a chromosome with both QTLs and genes (or the first one)
      const initial =
        list.find((c) => c.qtl_count > 0 && c.gene_count > 0) ?? list[0];
      setSelected(initial?.name ?? null);
    });
    return () => {
      cancelled = true;
    };
  }, [speciesId]);

  // Load summary when selected chromosome changes
  useEffect(() => {
    if (!selected) {
      setSummary(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    api.getChromosomeSummary(speciesId, selected, 200).then((data) => {
      if (cancelled) return;
      setSummary(data);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [speciesId, selected]);

  // Observe container width for responsive SVG
  useEffect(() => {
    if (!svgRef.current?.parentElement) return;
    const el = svgRef.current.parentElement;
    const obs = new ResizeObserver((entries) => {
      for (const e of entries) setWidth(Math.floor(e.contentRect.width));
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  // Layout constants
  const MARGIN_X = 12;
  const QTL_ROW_Y = 14;
  const QTL_ROW_H = 18;
  const CHROM_Y = 36;
  const CHROM_H = 10;
  const HIST_Y = 52;
  const HIST_H = 40;
  const AXIS_Y = 96;
  const totalH = 118;

  const chartW = Math.max(200, width - MARGIN_X * 2);

  const { maxGeneCount, ticks } = useMemo(() => {
    if (!summary) return { maxGeneCount: 1, ticks: [] as number[] };
    const m = Math.max(1, ...summary.gene_bins.map((b) => b.count));
    // Axis ticks at 0, 25%, 50%, 75%, 100%
    const positions = [0, 0.25, 0.5, 0.75, 1].map((f) =>
      Math.round(summary.length * f)
    );
    return { maxGeneCount: m, ticks: positions };
  }, [summary]);

  const xOf = (bp: number) => {
    if (!summary) return 0;
    return MARGIN_X + (bp / summary.length) * chartW;
  };

  const idx = chromosomes.findIndex((c) => c.name === selected);
  const prev = () => idx > 0 && setSelected(chromosomes[idx - 1].name);
  const next = () =>
    idx >= 0 && idx < chromosomes.length - 1 && setSelected(chromosomes[idx + 1].name);

  const chosen = chromosomes[idx];

  return (
    <div className="border-b border-gray-800 bg-gray-950 px-4 py-2">
      {/* Header row: chromosome picker + stats */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={prev}
            disabled={idx <= 0}
            className="rounded bg-gray-800 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 disabled:opacity-30"
          >
            ◀
          </button>
          <select
            value={selected ?? ""}
            onChange={(e) => setSelected(e.target.value)}
            className="rounded bg-gray-800 px-2 py-1 text-xs text-gray-100 font-mono"
          >
            {chromosomes.map((c) => (
              <option key={c.name} value={c.name}>
                {c.name}  ({humanBases(c.length)})
              </option>
            ))}
          </select>
          <button
            onClick={next}
            disabled={idx < 0 || idx >= chromosomes.length - 1}
            className="rounded bg-gray-800 px-2 py-1 text-xs text-gray-300 hover:bg-gray-700 disabled:opacity-30"
          >
            ▶
          </button>
        </div>
        {chosen && (
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>
              <span className="text-gray-500">Length: </span>
              <span className="text-gray-200 font-mono">
                {chosen.length.toLocaleString()} bp
              </span>
            </span>
            <span>
              <span className="text-gray-500">Genes: </span>
              <span className="text-emerald-300 font-mono">
                {chosen.gene_count.toLocaleString()}
              </span>
            </span>
            <span>
              <span className="text-gray-500">QTLs: </span>
              <span className="text-amber-300 font-mono">
                {chosen.qtl_count}
              </span>
            </span>
            {loading && <span className="text-gray-500">loading…</span>}
          </div>
        )}
      </div>

      {/* SVG ideogram */}
      <div className="relative mt-2">
        <svg
          ref={svgRef}
          width="100%"
          height={totalH}
          viewBox={`0 0 ${width} ${totalH}`}
          preserveAspectRatio="none"
          className="block"
        >
          {summary && (
            <>
              {/* Chromosome bar */}
              <rect
                x={MARGIN_X}
                y={CHROM_Y}
                width={chartW}
                height={CHROM_H}
                rx={CHROM_H / 2}
                fill="#374151"
                stroke="#4b5563"
              />

              {/* QTL ticks */}
              {summary.qtls.map((q) => {
                const x1 = xOf(q.start);
                const x2 = Math.max(x1 + 1, xOf(q.end));
                const color = CATEGORY_COLOR[q.trait_category] ?? CATEGORY_COLOR.Other;
                const wide = x2 - x1 > 1;
                return (
                  <g
                    key={q.id}
                    style={{ cursor: "pointer" }}
                    onClick={() => onNavigate(summary.chromosome, q.start, q.end)}
                    onMouseEnter={(e) => {
                      const rect = (e.target as SVGElement).getBoundingClientRect();
                      const parentRect = svgRef.current!.getBoundingClientRect();
                      setHover({
                        x: rect.left - parentRect.left + rect.width / 2,
                        y: 0,
                        text: `${q.trait}${q.breed ? ` · ${q.breed}` : ""} · ${q.start.toLocaleString()}-${q.end.toLocaleString()} · ${q.overlapping_gene_count} gene${q.overlapping_gene_count === 1 ? "" : "s"}`,
                      });
                    }}
                    onMouseLeave={() => setHover(null)}
                  >
                    {wide ? (
                      <rect
                        x={x1}
                        y={QTL_ROW_Y}
                        width={x2 - x1}
                        height={QTL_ROW_H}
                        fill={color}
                        opacity={0.65}
                      />
                    ) : (
                      <line
                        x1={x1}
                        x2={x1}
                        y1={QTL_ROW_Y}
                        y2={QTL_ROW_Y + QTL_ROW_H}
                        stroke={color}
                        strokeWidth={2}
                      />
                    )}
                  </g>
                );
              })}

              {/* Gene density histogram */}
              {summary.gene_bins.map((b, i) => {
                if (b.count === 0) return null;
                const x1 = xOf(b.start);
                const x2 = xOf(b.end);
                const h = (b.count / maxGeneCount) * HIST_H;
                return (
                  <rect
                    key={i}
                    x={x1}
                    y={HIST_Y + (HIST_H - h)}
                    width={Math.max(0.5, x2 - x1 - 0.2)}
                    height={h}
                    fill="#10b981"
                    opacity={0.75}
                    style={{ cursor: "pointer" }}
                    onClick={() => onNavigate(summary.chromosome, b.start, b.end)}
                    onMouseEnter={(e) => {
                      const rect = (e.target as SVGElement).getBoundingClientRect();
                      const parentRect = svgRef.current!.getBoundingClientRect();
                      setHover({
                        x: rect.left - parentRect.left + rect.width / 2,
                        y: 0,
                        text: `${b.count} gene${b.count === 1 ? "" : "s"} in ${humanBases(b.start)}–${humanBases(b.end)}${b.symbols.length ? ` · ${b.symbols.join(", ")}${b.count > b.symbols.length ? "…" : ""}` : ""}`,
                      });
                    }}
                    onMouseLeave={() => setHover(null)}
                  />
                );
              })}

              {/* Axis */}
              <line
                x1={MARGIN_X}
                x2={MARGIN_X + chartW}
                y1={AXIS_Y}
                y2={AXIS_Y}
                stroke="#4b5563"
              />
              {ticks.map((pos, i) => {
                const x = xOf(pos);
                return (
                  <g key={i}>
                    <line
                      x1={x}
                      x2={x}
                      y1={AXIS_Y}
                      y2={AXIS_Y + 4}
                      stroke="#6b7280"
                    />
                    <text
                      x={x}
                      y={AXIS_Y + 14}
                      textAnchor={i === 0 ? "start" : i === ticks.length - 1 ? "end" : "middle"}
                      fill="#9ca3af"
                      fontSize="10"
                      fontFamily="monospace"
                    >
                      {humanBases(pos)}
                    </text>
                  </g>
                );
              })}
            </>
          )}
        </svg>

        {/* Tooltip */}
        {hover && (
          <div
            className="pointer-events-none absolute z-10 whitespace-nowrap rounded bg-black px-2 py-1 text-[11px] text-white shadow-lg border border-gray-700"
            style={{
              left: Math.max(0, Math.min(width - 400, hover.x - 100)),
              top: -28,
            }}
          >
            {hover.text}
          </div>
        )}
      </div>
    </div>
  );
}
