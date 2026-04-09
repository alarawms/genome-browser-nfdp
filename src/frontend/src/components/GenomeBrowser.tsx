// Placeholder — replaced in Task 11 with JBrowse 2 integration
interface Props {
  speciesId: string;
  location: { chromosome: string; start: number; end: number } | null;
}

export default function GenomeBrowser({ speciesId, location }: Props) {
  return (
    <div className="flex h-full items-center justify-center bg-gray-900">
      <div className="text-center">
        <p className="text-lg text-gray-400">Genome Browser</p>
        <p className="mt-2 text-sm text-gray-500">
          Viewing: {speciesId}
          {location &&
            ` — Chr${location.chromosome}:${location.start.toLocaleString()}-${location.end.toLocaleString()}`}
        </p>
        <p className="mt-1 text-xs text-gray-600">
          JBrowse 2 integration coming in Task 11
        </p>
      </div>
    </div>
  );
}
