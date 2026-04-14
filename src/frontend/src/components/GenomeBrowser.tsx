import { useEffect, useRef, useState } from "react";
import { createViewState, JBrowseLinearGenomeView } from "@jbrowse/react-linear-genome-view";
import { api } from "../api/client";

interface Props {
  speciesId: string;
  location: { chromosome: string; start: number; end: number } | null;
}

export default function GenomeBrowser({ speciesId, location }: Props) {
  const [viewState, setViewState] = useState<ReturnType<typeof createViewState> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const prevSpecies = useRef(speciesId);

  // Load JBrowse config when species changes
  useEffect(() => {
    let cancelled = false;
    setError(null);

    api.getJBrowseConfig(speciesId).then((config) => {
      if (cancelled) return;
      try {
        const state = createViewState({
          assembly: config.assembly as any,
          tracks: config.tracks as any[],
          defaultSession: {
            // Session name varies with track count so JBrowse invalidates any
            // cached session that was built when fewer tracks existed.
            name: `${speciesId}-session-${config.tracks.length}`,
            view: {
              id: `${speciesId}-lgv`,
              type: "LinearGenomeView",
              tracks: config.tracks.map((t: any) => ({
                id: `${t.trackId}-shown`,
                type: t.type || "FeatureTrack",
                configuration: t.trackId,
                displays: [
                  {
                    id: `${t.trackId}-display-shown`,
                    type: "LinearBasicDisplay",
                    configuration: `${t.trackId}-LinearBasicDisplay`,
                  },
                ],
              })),
            },
          },
        });
        setViewState(state);
        prevSpecies.current = speciesId;
      } catch (e) {
        setError(`Failed to initialize genome view: ${e}`);
      }
    }).catch((e) => {
      if (!cancelled) setError(`Failed to load config: ${e.message}`);
    });

    return () => { cancelled = true; };
  }, [speciesId]);

  // Navigate when location changes
  useEffect(() => {
    if (!viewState || !location) return;
    try {
      viewState.session.view.navToLocString(
        `${location.chromosome}:${location.start}-${location.end}`,
      );
    } catch {
      // Location string may not match assembly — ignore
    }
  }, [viewState, location]);

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="rounded-lg bg-red-900/30 p-6 text-center">
          <p className="text-red-400">{error}</p>
          <p className="mt-2 text-sm text-gray-400">
            Make sure the backend is running and data is loaded (run `make data`)
          </p>
        </div>
      </div>
    );
  }

  if (!viewState) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-gray-400">Loading genome browser...</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto bg-white">
      <JBrowseLinearGenomeView viewState={viewState} />
    </div>
  );
}
