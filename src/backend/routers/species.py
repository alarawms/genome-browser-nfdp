from fastapi import APIRouter, Request

from src.backend.jbrowse_config import make_assembly_config, make_track_configs
from src.backend.models import Species

router = APIRouter(prefix="/api/species", tags=["species"])

SPECIES_INFO = [
    Species(
        id="sheep",
        name="Sheep",
        scientific_name="Ovis aries",
        assembly="Oar_rambouillet_v1.0",
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


@router.get("")
def list_species() -> list[Species]:
    return SPECIES_INFO


@router.get("/{species_id}/jbrowse-config")
def jbrowse_config(species_id: str, request: Request):
    base_url = str(request.base_url).rstrip("/") + "/data"
    assembly = make_assembly_config(species_id, base_url)
    tracks = make_track_configs(species_id, base_url)
    return {"assembly": assembly, "tracks": tracks}
