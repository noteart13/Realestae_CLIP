from fastapi import APIRouter, HTTPException, Query
from ..services.search_service import search_all
from ..services.embed_service import enrich_with_embeddings
from ..schemas import SearchResponse, Listing
from typing import List

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
def search(address: str = Query(..., description="Street address in AU")):
    results: List[Listing] = search_all(address)
    if not results:
        raise HTTPException(404, "No data found for the given address")
    return SearchResponse(query=address, results=results)

@router.get("/search+embed", response_model=SearchResponse)
def search_with_embed(address: str):
    results: List[Listing] = search_all(address)
    if not results:
        raise HTTPException(404, "No data found for the given address")
    results = [enrich_with_embeddings(r) for r in results]
    return SearchResponse(query=address, results=results)
