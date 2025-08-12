from typing import List
from ..schemas import Listing
from ..utils.config import settings
from ..scrapers import domain_au, realestate_au

def search_all(address: str) -> List[Listing]:
    dom = domain_au.search(address, max_images=settings.MAX_IMAGES)
    rea = realestate_au.search(address, max_images=settings.MAX_IMAGES)
    combined = dom + rea
    # ép về Pydantic model
    return [Listing(**item) for item in combined]
