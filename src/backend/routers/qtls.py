from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/species/{species_id}", tags=["qtls"])


@router.get("/qtls")
def get_qtls(
    species_id: str,
    request: Request,
    chromosome: str | None = None,
    start: int | None = None,
    end: int | None = None,
    trait_category: str | None = None,
    min_score: float | None = None,
    limit: int = 100,
    offset: int = 0,
):
    store = request.app.state.store
    return store.get_qtls(
        species_id,
        chromosome=chromosome,
        start=start,
        end=end,
        trait_category=trait_category,
        min_score=min_score,
        limit=limit,
        offset=offset,
    )


@router.get("/traits")
def get_traits(species_id: str, request: Request):
    store = request.app.state.store
    return store.get_traits(species_id)
