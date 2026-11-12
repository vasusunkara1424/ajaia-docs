"""Application factory.

- Mounts the JSON API under /api
- Maps domain errors to a consistent {"detail": {"code", "message"}} shape
- Serves the built React app (single deployable unit, no CORS in production)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, documents, shares
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.errors import DomainError
from app.services.seed import seed_demo_users


logger = logging.getLogger("ajaia")


def _check_production_config() -> None:
    settings = get_settings()
    if settings.environment != "production":
        return
    if settings.secret_key.startswith("dev-only"):
        raise RuntimeError("SECRET_KEY must be set in production.")
    if settings.sqlalchemy_url.startswith("sqlite"):
        logger.warning("Running production on SQLite: data is lost when the container restarts.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    _check_production_config()
    # Schema is created on boot; see ARCHITECTURE.md for why there are no migrations yet.
    Base.metadata.create_all(bind=engine)
    if get_settings().seed_demo_users:
        with SessionLocal() as db:
            seed_demo_users(db)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

    if settings.environment == "development":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    _register_error_handlers(app)

    api = APIRouter(prefix="/api")
    api.include_router(auth.router)
    api.include_router(documents.router)
    api.include_router(shares.router)

    @api.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api)
    _mount_frontend(app, settings)
    return app


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", []) if p != "body")
        message = f"{field}: {first.get('msg', 'Invalid input')}" if field else "Invalid input."
        return JSONResponse(
            status_code=422,
            content={"detail": {"code": "validation_failed", "message": message}},
        )


def _mount_frontend(app: FastAPI, settings) -> None:
    dist = settings.frontend_dist
    index = dist / "index.html"
    if not index.exists():
        return  # API-only mode (local dev runs Vite separately)

    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        # Unknown /api paths should 404 as JSON, not return the SPA shell.
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=404, content={"detail": {"code": "not_found", "message": "Not found."}}
            )
        candidate = (dist / full_path).resolve()
        if full_path and candidate.is_file() and dist.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(index)


app = create_app()
