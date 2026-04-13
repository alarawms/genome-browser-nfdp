import { useState } from "react";
import { useSpecies } from "./hooks/useSpecies";
import SpeciesSelector from "./components/SpeciesSelector";
import QtlExplorer from "./components/QtlExplorer";
import GenomeBrowser from "./components/GenomeBrowser";
import SearchBar from "./components/SearchBar";
import ChromosomeOverview from "./components/ChromosomeOverview";

export default function App() {
  const { species, selectedId, select, loading } = useSpecies();
  const [location, setLocation] = useState<{
    chromosome: string;
    start: number;
    end: number;
  } | null>(null);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-800 bg-gray-900 px-4 py-3">
        <h1 className="text-lg font-bold text-emerald-400">
          Saudi Livestock Genome Browser
        </h1>
        <div className="flex items-center gap-4">
          <SpeciesSelector
            species={species}
            selectedId={selectedId}
            onSelect={select}
          />
          <SearchBar
            speciesId={selectedId}
            onNavigate={(chr, start, end) =>
              setLocation({ chromosome: chr, start, end })
            }
          />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-72 overflow-y-auto border-r border-gray-800 bg-gray-900">
          <QtlExplorer
            speciesId={selectedId}
            onQtlClick={(chr, start, end) =>
              setLocation({ chromosome: chr, start, end })
            }
          />
        </aside>

        {/* Genome Browser (with chromosome overview on top) */}
        <main className="flex flex-1 flex-col overflow-hidden">
          <ChromosomeOverview
            speciesId={selectedId}
            onNavigate={(chr, start, end) =>
              setLocation({ chromosome: chr, start, end })
            }
          />
          <div className="flex-1 overflow-hidden">
            <GenomeBrowser speciesId={selectedId} location={location} />
          </div>
        </main>
      </div>
    </div>
  );
}
