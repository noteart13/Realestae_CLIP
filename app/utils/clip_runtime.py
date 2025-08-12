import torch
import clip
from PIL import Image
from io import BytesIO
from .config import settings
from . import http

_model = None
_preprocess = None
_device = None

def _resolve_device():
    if settings.CLIP_DEVICE == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if settings.CLIP_DEVICE == "cpu":
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"

def load_clip():
    global _model, _preprocess, _device
    if _model is None:
        _device = _resolve_device()
        _model, _preprocess = clip.load(settings.CLIP_MODEL, device=_device)
    return _model, _preprocess, _device

def embed_image_url(url: str) -> list[float] | None:
    model, preprocess, device = load_clip()
    try:
        resp = http.get(url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        tensor = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            feats = model.encode_image(tensor)
        return feats[0].cpu().numpy().tolist()
    except Exception:
        return None
