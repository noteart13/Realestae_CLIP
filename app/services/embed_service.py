# app/services/embed_service.py
from ..schemas import Listing, ListingImage
from ..utils.clip_runtime import embed_image_url

def enrich_with_embeddings(listing: Listing) -> Listing:
    imgs = []
    for img in listing.images:
        emb = embed_image_url(str(img.url))
        imgs.append(ListingImage(url=img.url, embedding=emb))
    listing.images = imgs
    return listing
