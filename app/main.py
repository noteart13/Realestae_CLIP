from fastapi import FastAPI
from .api.routes import router
from .utils.config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "env": settings.ENV}
