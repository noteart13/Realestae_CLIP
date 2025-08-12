import random, time
import requests
from requests.adapters import HTTPAdapter, Retry
from .config import settings

_session = None

def _pick_ua():
    if settings.ROTATE_UA and settings.UA_POOL:
        return random.choice(settings.UA_POOL)
    return settings.USER_AGENT

def get_session():
    global _session
    if _session is None:
        s = requests.Session()
        retries = Retry(
            total=settings.HTTP_RETRIES,
            backoff_factor=0.0,               # ta tự backoff có kiểm soát
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=["GET","HEAD"]
        )
        s.headers.update({"User-Agent": _pick_ua(),
                          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                          "Accept-Language": settings.HTTP_LANG})
        if settings.PROXY_URL:
            s.proxies.update({"http": settings.PROXY_URL, "https": settings.PROXY_URL})
        s.mount("https://", HTTPAdapter(max_retries=retries))
        s.mount("http://", HTTPAdapter(max_retries=retries))
        _session = s
    return _session

def get(url: str, **kwargs) -> requests.Response | None:
    s = get_session()
    timeout = kwargs.pop("timeout", (6, settings.HTTP_TIMEOUT))
    attempts = 0
    while True:
        try:
            # delay ngẫu nhiên trước mỗi lần bắn
            time.sleep(random.uniform(settings.REQUEST_DELAY_MIN, settings.REQUEST_DELAY_MAX))
            # đổi UA mỗi lần nếu bật rotate
            s.headers["User-Agent"] = _pick_ua()
            resp = s.get(url, timeout=timeout, **kwargs)
            # nếu 429 → backoff thủ công rồi thử lại
            if resp.status_code == 429 and attempts < settings.MAX_BACKOFF_ATTEMPTS:
                delay = (settings.BACKOFF_BASE ** attempts) + random.uniform(0, 0.7)
                time.sleep(delay)
                attempts += 1
                continue
            return resp
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.SSLError):
            if attempts >= settings.MAX_BACKOFF_ATTEMPTS:
                return None
            delay = (settings.BACKOFF_BASE ** attempts) + random.uniform(0, 0.7)
            time.sleep(delay)
            attempts += 1
