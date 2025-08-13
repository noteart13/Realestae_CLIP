# app/schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ListingImage(BaseModel):
    url: HttpUrl
    embedding: Optional[List[float]] = None  # 512-d for ViT-B/32

class Listing(BaseModel):
    source: str
    address: Optional[str] = None
    price: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    propertyType: Optional[str] = None
    url: Optional[HttpUrl] = None
    images: List[ListingImage] = []

class SearchResponse(BaseModel):
    query: str
    results: List[Listing]
