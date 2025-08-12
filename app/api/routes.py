from typing import List, Dict, Optional
from fastapi import APIRouter, Query
from ..services.search_service import search_all
from ..services.embed_service import enrich_with_embeddings
from ..schemas import SearchResponse, Listing

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
def search(address: str, use_mock: bool|None=None, max_results: int|None=None, max_images: int|None=None,
           return_urls: bool=False):
    from ..scrapers.find_urls import search_address
    urls = search_address(address, max_results=max_results or 1)
    from ..services.search_service import search_all
    results = search_all(address, use_mock=use_mock, max_results=max_results, max_images=max_images)
    if return_urls:
        # nhét tạm vào field price để bạn nhìn nhanh (hoặc thêm field phụ trong schema nếu muốn)
        for r in results:
            if not r.price:
                r.price = f"urls: {urls}"
    return SearchResponse(query=address, results=results)


@router.get("/search+embed", response_model=SearchResponse, summary="Search + CLIP embeddings")
def search_with_embed(
    address: str,
    use_mock: Optional[bool] = None,
    max_results: Optional[int] = Query(None, ge=1, le=10),
    max_images: Optional[int] = Query(None, ge=0, le=10),
):
    results: List[Listing] = search_all(
        address,
        use_mock=use_mock,
        max_results=max_results,
        max_images=max_images,
    )
    results = [enrich_with_embeddings(r) for r in results]
    return SearchResponse(query=address, results=results)

@router.get("/urls", summary="Show candidate listing URLs")
def urls(address: str) -> Dict[str, List[str]]:
    """Trả về các URL tìm được từ DuckDuckGo (realestate.com.au/domain.com.au)."""
    from ..scrapers.find_urls import search_address
    return search_address(address)
