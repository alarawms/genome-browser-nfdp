import { QTL } from "../api/client";

interface Props {
  qtl: QTL;
  onNavigate: (chr: string, start: number, end: number) => void;
}

export default function QtlDetail({ qtl, onNavigate }: Props) {
  return (
    <button
      onClick={() => onNavigate(qtl.chromosome, qtl.start, qtl.end)}
      className="w-full rounded-md bg-gray-800 p-3 text-left transition-colors hover:bg-gray-750 border-l-[3px]"
      style={{
        borderLeftColor: categoryColor(qtl.trait_category),
      }}
    >
      <p className="text-sm font-semibold text-white">{qtl.trait}</p>
      <p className="mt-1 text-xs text-gray-400">
        Chr{qtl.chromosome}:{qtl.start.toLocaleString()}-{qtl.end.toLocaleString()}
      </p>
      <div className="mt-1 flex items-center gap-2 text-xs">
        {qtl.score != null && (
          <span style={{ color: categoryColor(qtl.trait_category) }}>
            Score: {qtl.score}
          </span>
        )}
        {qtl.pubmed_id && (
          <a
            href={`https://pubmed.ncbi.nlm.nih.gov/${qtl.pubmed_id}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline"
            onClick={(e) => e.stopPropagation()}
          >
            PMID:{qtl.pubmed_id}
          </a>
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
    Other: "#94a3b8",
  };
  return colors[category] ?? colors.Other;
}
