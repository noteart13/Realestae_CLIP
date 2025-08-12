from typing import Dict, List
from bs4 import BeautifulSoup
import json
from ..utils import http
from .common import parse_next_data

def fetch(url: str, max_images: int = 5) -> Dict:
    resp = http.get(url)
    if resp is None or resp.status_code != 200:
        return {}

    # thử lấy NEXT_DATA
    data = parse_next_data(resp.text)
    images = []
    address = price = beds = baths = ptype = None

    if data:
        comp = (data.get("props") or {}).get("pageProps", {}).get("componentProps") or {}
        address = (comp.get("address") or {}).get("streetAddress") if isinstance(comp.get("address"), dict) else comp.get("address")
        price = comp.get("price") or comp.get("advertisedPrice")
        beds  = comp.get("beds") or comp.get("bedrooms")
        baths = comp.get("baths") or comp.get("bathrooms")
        ptype = comp.get("propertyType")
        gallery = comp.get("gallery") or comp.get("images") or []
        for g in gallery[:max_images]:
            u = g.get("url") if isinstance(g, dict) else g
            if u: images.append({"url": u})

    # nếu NEXT_DATA không có, fallback HTML
    if not address:
        soup = BeautifulSoup(resp.text, "lxml")
        h = soup.find("meta", property="og:title")
        if h and h.get("content"): address = h["content"]
    return {
        "source": "domain.com.au",
        "address": address,
        "price": price,
        "bedrooms": beds,
        "bathrooms": baths,
        "propertyType": ptype,
        "url": url,
        "images": images,
    }
