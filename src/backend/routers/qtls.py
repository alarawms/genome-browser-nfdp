from fastapi import APIRouter, HTTPException, Request

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


@router.get("/chromosomes")
def list_chromosomes(species_id: str, request: Request):
    """Return chromosomes for a species with length + gene count + QTL count."""
    store = request.app.state.store
    return store.list_chromosomes(species_id)


@router.get("/chromosome/{chrom}/summary")
def chromosome_summary(species_id: str, chrom: str, request: Request, bins: int = 200):
    """Binned gene density + full QTL list for one chromosome."""
    store = request.app.state.store
    result = store.chromosome_summary(species_id, chrom, bins=bins)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No length info for {species_id}/{chrom}",
        )
    return result
