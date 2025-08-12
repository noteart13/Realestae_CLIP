# app/services/search_service.py
from typing import List, Optional
from ..schemas import Listing
from ..utils.config import settings
from ..scrapers import domain_au, realestate_au
from ..scrapers.find_urls import search_address as find_urls

def search_all(
    address: str,
    use_mock: Optional[bool] = None,
    max_results: Optional[int] = None,
    max_images: Optional[int] = None,
) -> List[Listing]:
    """
    Tìm URL từ DDG -> fetch chi tiết từ từng site -> hợp nhất kết quả.
    - use_mock: None => tự quyết theo ENV=local, True/False => override
    - max_results: số URL mỗi site
    - max_images: số ảnh mỗi listing
    """
    # cấu hình hiệu lực
    mr = max_results or settings.MAX_RESULTS
    mi = max_images or settings.MAX_IMAGES
    mock = (settings.ENV.lower() == "local") if use_mock is None else bool(use_mock)

    items: List[Listing] = []

    # 1) Tìm URL từ DDG
    urls = find_urls(address, max_results=mr)

    # 2) realestate.com.au
    for u in urls.get("realestate", []):
        try:
            d = realestate_au.fetch(u, max_images=mi)
            if d and (d.get("address") or d.get("images")):
                items.append(Listing(**d))
        except Exception:
            # an toàn: không cho lỗi văng ra ngoài
            continue

    # 3) domain.com.au
    for u in urls.get("domain", []):
        try:
            d = domain_au.fetch(u, max_images=mi)
            if d and (d.get("address") or d.get("images")):
                items.append(Listing(**d))
        except Exception:
            continue

    # 4) fallback mock khi local (để demo)
    if not items and mock:
        items.append(Listing(
            source="mock",
            address=address,
            price="Contact agent",
            bedrooms=2,
            bathrooms=1,
            propertyType="Unit",
            url="https://example.com/mock",
            images=[],
        ))

    return items
