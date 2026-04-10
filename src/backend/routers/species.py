import os

from fastapi import APIRouter

from src.backend.jbrowse_config import make_assembly_config, make_track_configs, get_species_meta
from src.backend.models import Species

router = APIRouter(prefix="/api/species", tags=["species"])

_BUILTIN_SPECIES = [
    Species(
        id="sheep",
        name="Sheep",
        scientific_name="Ovis aries",
        assembly="ARS-UI_Ramb_v3.0",
        chromosome_count=27,
    ),
    Species(
        id="goat",
        name="Goat",
        scientific_name="Capra hircus",
        assembly="CHIR_1.0",
        chromosome_count=30,
    ),
]


def _get_all_species() -> list[Species]:
    """Built-in species + any user-added genomes from data/genomes.json."""
    data_dir = os.environ.get("DATA_DIR", "data")
    meta = get_species_meta(data_dir)
    builtin_ids = {s.id for s in _BUILTIN_SPECIES}
    result = list(_BUILTIN_SPECIES)
    for sid, info in meta.items():
        if sid not in builtin_ids:
            result.append(Species(
                id=sid,
                name=info.get("name", sid),
                scientific_name=info.get("scientific_name", ""),
                assembly=info["assembly_name"],
                chromosome_count=info.get("chromosome_count", 0),
            ))
    return result


@router.get("")
def list_species() -> list[Species]:
    return _get_all_species()


@router.get("/{species_id}/jbrowse-config")
def jbrowse_config(species_id: str):
    data_dir = os.environ.get("DATA_DIR", "data")
    # Use relative URLs so JBrowse requests go through the frontend proxy
    base_url = "/data"
    assembly = make_assembly_config(species_id, base_url, data_dir)
    tracks = make_track_configs(species_id, base_url, data_dir)
    return {"assembly": assembly, "tracks": tracks}
