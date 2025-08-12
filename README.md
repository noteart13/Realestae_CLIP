# Realestate CLIP API

## Local
```bash
python -m venv .venv 
.venv\Scripts\Activate.ps1 
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://localhost:8000/docs
