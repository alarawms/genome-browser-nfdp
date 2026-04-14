from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(q: str, request: Request, species: str | None = None, limit: int = 50):
    store = request.app.state.store
    return store.search(q, species_id=species, limit=limit)
