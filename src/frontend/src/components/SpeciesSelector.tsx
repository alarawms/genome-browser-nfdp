import { Species } from "../api/client";

interface Props {
  species: Species[];
  selectedId: string;
  onSelect: (id: string) => void;
}

export default function SpeciesSelector({ species, selectedId, onSelect }: Props) {
  return (
    <div className="flex gap-1 rounded-lg border border-blue-500/30 bg-gray-800 p-1">
      {species.map((s) => (
        <button
          key={s.id}
          onClick={() => onSelect(s.id)}
          className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
            s.id === selectedId
              ? "bg-blue-600 text-white"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {s.name}
        </button>
      ))}
    </div>
  );
}
