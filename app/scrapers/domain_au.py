from typing import List, Dict
from ..utils import http
from .common import parse_next_data

def search(address: str, max_images: int = 5) -> List[Dict]:
    # demo: dùng trang search có query string tối giản
    url = f"https://www.domain.com.au/?mode=buy&address={address}"
    resp = http.get(url)
    if resp.status_code != 200:
        return []

    data = parse_next_data(resp.text)
    if not data:
        return []

    # tuỳ phiên bản Domain, đường dẫn JSON có thể đổi — ta truy thủ một vài key phổ biến
    props = (data.get("props") or {}).get("pageProps") or {}
    listings = []
    # cố gắng tìm một mảng listing trong props
    for k, v in props.items():
        if isinstance(v, list):
            for item in v:
                listings.append(item)
        elif isinstance(v, dict) and "listings" in v and isinstance(v["listings"], list):
            listings.extend(v["listings"])

    results = []
    for it in listings[:3]:  # giới hạn vài kết quả đầu
        images = []
        gallery = (it.get("gallery") or it.get("images") or [])
        for img in gallery[:max_images]:
            u = img.get("url") if isinstance(img, dict) else img
            if u:
                images.append({"url": u})
        results.append({
            "source": "domain.com.au",
            "address": (it.get("address") or {}).get("streetAddress") if isinstance(it.get("address"), dict) else it.get("address"),
            "price": it.get("price") or it.get("advertisedPrice"),
            "bedrooms": it.get("beds") or it.get("bedrooms"),
            "bathrooms": it.get("baths") or it.get("bathrooms"),
            "propertyType": it.get("propertyType"),
            "url": it.get("url") or it.get("canonicalUrl"),
            "images": images
        })
    return results
