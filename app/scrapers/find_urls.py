# app/scrapers/find_urls.py
import re, time, random
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, unquote, urlunparse, urlencode
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from app.utils import config as cfg

RE_URL_REA = re.compile(
    r"^https?://(?:www\.)?realestate\.com\.au/(?:property-|buy/|project/|new-home/|sold/|rent/)[^\s]+",
    re.I,
)
RE_URL_DOM = re.compile(
    r"^https?://(?:www\.)?domain\.com\.au/(?:property-|sale/|rent/|project/|new-home/|sold/)[^\s]+",
    re.I,
)

SEARCH_RETRIES = getattr(cfg.settings, "SEARCH_RETRIES", 4)
BACKOFF_BASE   = getattr(cfg.settings, "SEARCH_BACKOFF_BASE", 1.8)
MAX_RESULTS_DEFAULT = getattr(cfg.settings, "MAX_RESULTS", 3)

STRIP_QUERY_KEYS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content",
                    "src","sclid","rsf","ref","gclid","ocid","cid","eid","bidId","from"}

def _normalize_ddg_href(href: str) -> str:
    if not href:
        return ""
    if href.startswith("/"):
        href = urljoin("https://duckduckgo.com", href)
    try:
        u = urlparse(href)
        if u.netloc.endswith("duckduckgo.com") and u.path.startswith("/l/"):
            qs = parse_qs(u.query)
            if "uddg" in qs: return unquote(qs["uddg"][0])
        if u.netloc.endswith("duckduckgo.com") and u.path.startswith("/r.jina.ai/"):
            rest = href.split("/r.jina.ai/", 1)[-1]
            if rest.startswith("http"): return rest
    except Exception:
        pass
    return href

def _canonicalize_url(raw: str) -> str:
    try:
        u = urlparse(raw)
        if not (u.netloc.endswith("realestate.com.au") or u.netloc.endswith("domain.com.au")):
            return raw
        q = parse_qs(u.query)
        q = {k: v for k, v in q.items() if k not in STRIP_QUERY_KEYS}
        query = urlencode({k: v[0] if len(v)==1 else v for k,v in q.items()}, doseq=True)
        path = re.sub(r"/{2,}", "/", u.path).rstrip("/") or "/"
        return urlunparse((u.scheme or "https", u.netloc.lower(), path, "", query, ""))
    except Exception:
        return raw

def _httpx_client() -> httpx.Client:
    proxies = None
    if getattr(cfg.settings, "PROXY_URL", ""):
        proxies = {"http": cfg.settings.PROXY_URL, "https": cfg.settings.PROXY_URL}
    headers = {
        "User-Agent": cfg.settings.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": getattr(cfg.settings, "HTTP_LANG", "en-AU,en;q=0.8"),
        "Connection": "keep-alive",
    }
    return httpx.Client(
        timeout=httpx.Timeout(6.0, read=getattr(cfg.settings, "HTTP_TIMEOUT", 20)),
        headers=headers,
        follow_redirects=True,
        proxies=proxies,
        verify=getattr(cfg.settings, "HTTP_VERIFY", True),
    )

def _html_ddg_client() -> httpx.Client:
    c = _httpx_client()
    c.timeout = httpx.Timeout(8.0, read=25.0)
    return c

def _ddg_html_fallback(query: str, max_results: int) -> List[str]:
    bases = ["https://html.duckduckgo.com/html/",
             "https://duckduckgo.com/html/",
             "https://lite.duckduckgo.com/lite/"]
    for base in bases:
        try:
            with _html_ddg_client() as c:
                r = c.get(base, params={"q": query, "kl": (getattr(cfg.settings, "DDG_REGION", "") or "wt-wt")})
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "lxml")
                urls: List[str] = []
                for a in soup.select("a.result__a[href], a.result__url[href], a[href].result__a, a[href].result__snippet"):
                    href = _normalize_ddg_href(a.get("href","").strip())
                    if href:
                        urls.append(href)
                        if len(urls) >= max_results: break
                if urls: return urls
        except Exception:
            continue
    return []

def _ddg_text(query: str, max_results: int) -> List[str]:
    attempt = 0
    while True:
        try:
            urls: List[str] = []
            with DDGS() as ddgs:
                for r in ddgs.text(
                    query,
                    region=(getattr(cfg.settings, "DDG_REGION", "") or "wt-wt"),
                    safesearch="off",
                    timelimit=None,
                    max_results=max_results * 5,
                ):
                    href = (r.get("href") or r.get("link") or "").strip()
                    href = _normalize_ddg_href(href)
                    if href:
                        urls.append(href)
                        if len(urls) >= max_results: break
            return urls
        except RatelimitException:
            if attempt >= SEARCH_RETRIES:
                return _ddg_html_fallback(query, max_results)
            time.sleep((BACKOFF_BASE ** attempt) + random.uniform(0, 0.5))
            attempt += 1
        except Exception:
            return _ddg_html_fallback(query, max_results)

def _variants(address: str) -> List[str]:
    a = address.strip()
    outs = {a}
    outs.add(re.sub(r"^\s*\d+\s*/\s*", "", a))
    outs.add(re.sub(r"\b\d{4}\b", "", a).strip())
    outs.add(re.sub(r"^\s*\d+[^A-Za-z]+", "", a).strip())
    outs.add(a.replace(" QLD ", " Qld "))
    outs.add(a.replace(" Qld ", " QLD "))
    return [s for s in outs if s]

def _dedupe_host_path(urls: List[str]) -> List[str]:
    seen, out = set(), []
    for u in urls:
        cu = _canonicalize_url(u)
        p = urlparse(cu)
        key = (p.netloc.lower(), p.path.rstrip("/"))
        if key not in seen:
            seen.add(key); out.append(cu)
    return out

def _filter_and_take(urls: List[str], pattern: re.Pattern, limit: int) -> List[str]:
    out = []
    for href in urls:
        href = _canonicalize_url(_normalize_ddg_href(href))
        if pattern.match(href):
            out.append(href)
            if len(out) >= limit: break
    return out

def _probe_urls(urls: List[str], limit: int) -> List[str]:
    good: List[str] = []
    if not urls: return good
    try:
        with _httpx_client() as c:
            for u in urls:
                if len(good) >= limit: break
                try:
                    r = c.head(u)
                    if r.status_code == 405:
                        r = c.get(u)
                    if 200 <= r.status_code < 400:
                        good.append(str(r.url))
                except Exception:
                    continue
    except Exception:
        pass
    return good[:limit]

def search_address(address: str, max_results: int | None = None) -> Dict[str, List[str]]:
    max_results = max_results or MAX_RESULTS_DEFAULT
    urls_rea: List[str] = []
    urls_dom: List[str] = []

    for q in _variants(address):
        if len(urls_rea) < max_results:
            raw = _ddg_text(f'{q} site:realestate.com.au', max_results * 3)
            cand = _filter_and_take(raw, RE_URL_REA, max_results * 2)
            urls_rea.extend(cand)
            urls_rea = _dedupe_host_path(urls_rea)[:max_results]
        time.sleep(0.5)
        if len(urls_dom) < max_results:
            raw = _ddg_text(f'{q} site:domain.com.au', max_results * 3)
            cand = _filter_and_take(raw, RE_URL_DOM, max_results * 2)
            urls_dom.extend(cand)
            urls_dom = _dedupe_host_path(urls_dom)[:max_results]
        if len(urls_rea) >= max_results and len(urls_dom) >= max_results:
            break

    urls_rea = _probe_urls(_dedupe_host_path(urls_rea), max_results) or urls_rea[:max_results]
    urls_dom = _probe_urls(_dedupe_host_path(urls_dom), max_results) or urls_dom[:max_results]

    return {"realestate": _dedupe_host_path(urls_rea)[:max_results],
            "domain":     _dedupe_host_path(urls_dom)[:max_results]}
