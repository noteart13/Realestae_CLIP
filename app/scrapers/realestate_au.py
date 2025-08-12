from typing import List, Dict
from ..utils import http
from .common import extract_json_by_regex

PATTERN = r"window\.ArgonautExchange\s*=\s*(\{.*?\});"

def search(address: str, max_images: int = 5) -> List[Dict]:
    # tạo query “mềm” để trang vẫn trả dữ liệu; có thể thay bằng builder cụ thể hơn
    q = address.replace(" ", "+")
    url = f"https://www.realestate.com.au/buy/?query={q}"
    resp = http.get(url)
    if resp.status_code != 200:
        return []

    data = extract_json_by_regex(resp.text, PATTERN)
    if not data:
        return []

    cache = (data.get("resi-property_listing-experience-web") or {}).get("urqlClientCache") or {}
    # gom các blob data
    blobs = []
    for v in cache.values():
        d = v.get("data")
        if isinstance(d, str):
            blobs.append(d)

    import json
    results: List[Dict] = []
    for blob in blobs:
        try:
            dd = json.loads(blob)
        except Exception:
            continue
        listing = (dd.get("details") or {}).get("listing") or {}
        if not listing:
            continue
        media = (listing.get("media") or {}).get("images") or []
        images = []
        for m in media[:max_images]:
            u = m.get("url") or m.get("templatedUrl")
            if u:
                images.append({"url": u})
        details = listing.get("propertyDetails") or {}
        addr = (listing.get("address") or {}).get("display", {}).get("fullAddress")
        results.append({
            "source": "realestate.com.au",
            "address": addr,
            "price": listing.get("price") or listing.get("advertising", {}).get("price"),
            "bedrooms": details.get("bedrooms"),
            "bathrooms": details.get("bathrooms"),
            "propertyType": details.get("propertyType"),
            "url": listing.get("canonicalUrl") or listing.get("seo", {}).get("canonicalUrl"),
            "images": images
        })
        if len(results) >= 3:
            break
    return results
