from typing import Dict, List
import re, json
from ..utils import http

PATTERN = r"window\.ArgonautExchange\s*=\s*(\{.*?\});"

def fetch(url: str, max_images: int = 5) -> Dict:
    resp = http.get(url)
    if resp is None or resp.status_code != 200:
        return {}
    text = resp.text
    m = re.search(PATTERN, text, re.S)
    images = []
    address = price = beds = baths = ptype = None

    if m:
        try:
            data = json.loads(m.group(1))
            cache = (data.get("resi-property_listing-experience-web") or {}).get("urqlClientCache") or {}
            for v in cache.values():
                d = v.get("data")
                if not isinstance(d, str): continue
                dd = json.loads(d)
                listing = (dd.get("details") or {}).get("listing") or {}
                if not listing: continue
                details = listing.get("propertyDetails") or {}
                address = (listing.get("address") or {}).get("display", {}).get("fullAddress")
                price = listing.get("price") or listing.get("advertising", {}).get("price")
                beds  = details.get("bedrooms")
                baths = details.get("bathrooms")
                ptype = details.get("propertyType")
                media = (listing.get("media") or {}).get("images") or []
                for m2 in media[:max_images]:
                    u = m2.get("url") or m2.get("templatedUrl")
                    if u: images.append({"url": u})
                break
        except Exception:
            pass

    return {
        "source": "realestate.com.au",
        "address": address,
        "price": price,
        "bedrooms": beds,
        "bathrooms": baths,
        "propertyType": ptype,
        "url": url,
        "images": images,
    }
