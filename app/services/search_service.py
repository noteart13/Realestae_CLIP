from typing import List
from ..schemas import Listing
from ..utils.config import settings
from ..scrapers import domain_au, realestate_au
from ..scrapers.find_urls import search_address as find_urls

def search_all(address: str) -> List[Listing]:
    urls = find_urls(address, max_results=settings.MAX_RESULTS)
    items = []

    # realestate.com.au
    for u in urls.get("realestate", []):
        d = realestate_au.fetch(u, max_images=settings.MAX_IMAGES)
        if d and (d.get("address") or d.get("images")):
            items.append(Listing(**d))

    # domain.com.au
    for u in urls.get("domain", []):
        d = domain_au.fetch(u, max_images=settings.MAX_IMAGES)
        if d and (d.get("address") or d.get("images")):
            items.append(Listing(**d))

    # fallback mock trong local (tuỳ chọn)
    if not items and settings.ENV.lower() == "local":
        items.append(Listing(
            source="mock",
            address=address,
            price="Contact agent",
            bedrooms=2, bathrooms=1, propertyType="Unit",
            url="https://example.com/mock",
            images=[]
        ))
    return items
