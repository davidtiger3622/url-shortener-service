from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.docs import custom_docs
from app.limiter import limiter
from app.routers import analytics, auth, links, redirect

app = FastAPI(
    title="URL Shortener Service",
    description="A backend service for shortening URLs, tracking clicks, and viewing link analytics.",
    version="1.0.0",
    docs_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(analytics.router)

@app.get("/docs", include_in_schema=False)
def docs():
    return custom_docs()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(redirect.router)
