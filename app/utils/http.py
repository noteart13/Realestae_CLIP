import requests
from requests.adapters import HTTPAdapter, Retry
from .config import settings

_session = None

def get_session():
    global _session
    if _session is None:
        s = requests.Session()
        retries = Retry(
            total=settings.HTTP_RETRIES,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=["GET","HEAD"]
        )
        s.headers.update({"User-Agent": settings.USER_AGENT})
        s.mount("https://", HTTPAdapter(max_retries=retries))
        s.mount("http://", HTTPAdapter(max_retries=retries))
        _session = s
    return _session

def get(url: str, **kwargs) -> requests.Response:
    s = get_session()
    kwargs.setdefault("timeout", settings.HTTP_TIMEOUT)
    return s.get(url, **kwargs)
