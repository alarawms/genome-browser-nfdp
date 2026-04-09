import json
from pathlib import Path

import pandas as pd


class DataStore:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._qtl_frames: dict[str, pd.DataFrame] = {}
        self._load_all()

    def _load_all(self):
        qtl_dir = self.data_dir / "qtl"
        if not qtl_dir.exists():
            return
        for species_dir in qtl_dir.iterdir():
            if not species_dir.is_dir():
                continue
            json_path = species_dir / "qtls.json"
            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
                if data:
                    self._qtl_frames[species_dir.name] = pd.DataFrame(data)

    def get_qtls(
        self,
        species_id: str,
        chromosome: str | None = None,
        start: int | None = None,
        end: int | None = None,
        trait_category: str | None = None,
        min_score: float | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        df = self._qtl_frames.get(species_id)
        if df is None or df.empty:
            return []

        mask = pd.Series(True, index=df.index)
        if chromosome is not None:
            mask &= df["chromosome"] == chromosome
        if start is not None:
            mask &= df["end"] >= start
        if end is not None:
            mask &= df["start"] <= end
        if trait_category is not None:
            mask &= df["trait_category"] == trait_category
        if min_score is not None and "score" in df.columns:
            mask &= df["score"] >= min_score

        result = df[mask].iloc[offset : offset + limit]
        return result.to_dict(orient="records")

    def get_traits(self, species_id: str) -> list[dict]:
        df = self._qtl_frames.get(species_id)
        if df is None or df.empty:
            return []

        grouped = df.groupby("trait_category").agg(
            qtl_count=("id", "count"),
            name=("trait_category", "first"),
        )
        return [
            {"name": row["name"], "category": cat, "qtl_count": row["qtl_count"]}
            for cat, row in grouped.iterrows()
        ]

    def search(
        self, query: str, species_id: str | None = None
    ) -> list[dict]:
        results = []
        q = query.lower()
        for sid, df in self._qtl_frames.items():
            if species_id and sid != species_id:
                continue
            matches = df[df["trait"].str.lower().str.contains(q, na=False)]
            for _, row in matches.iterrows():
                results.append(
                    {
                        "type": "qtl",
                        "species_id": sid,
                        "label": f"{row['trait']} QTL",
                        "chromosome": row["chromosome"],
                        "start": int(row["start"]),
                        "end": int(row["end"]),
                    }
                )
        return results
