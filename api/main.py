"""FastAPI REST API Application Entrypoint for CustomerAtlas Enterprise Platform.

Provides high-performance, validated, documented REST endpoints under /api/v1
serving Customer 360, Segments, Analytics, ML Inference, and System Health.
"""

import sys
import time
from pathlib import Path

# Ensure root and streamlit_app are in sys.path for unified service and config discovery
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "streamlit_app"
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes.customers import router as customers_router
from api.routes.segments import router as segments_router
from api.routes.analytics import router as analytics_router
from api.routes.ml import router as ml_router
from api.routes.system import router as system_router
from config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION
from utils.exceptions import CustomerAtlasError, DataValidationError, ModelLoadError, ModelInferenceError
from utils.logging_config import logger


def create_app() -> FastAPI:
    """FastAPI application factory with enterprise configuration and middleware."""
    app = FastAPI(
        title=f"{APP_NAME} Enterprise REST API",
        description=f"{APP_DESCRIPTION}. Production-grade API endpoints for Customer 360, audience segmentation, forward CLV, and churn intelligence.",
        version=APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Global CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Processing & Timing Middleware
    @app.middleware("http")
    async def log_and_time_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        response.headers["X-Application-Version"] = APP_VERSION
        return response

    # Centralized Custom Exception Handlers
    @app.exception_handler(DataValidationError)
    async def data_validation_exception_handler(request: Request, exc: DataValidationError):
        logger.warning(f"Data validation error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "error": "DataValidationError", "detail": str(exc)},
        )

    @app.exception_handler(ModelLoadError)
    async def model_load_exception_handler(request: Request, exc: ModelLoadError):
        logger.error(f"Model load error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"success": False, "error": "ModelLoadError", "detail": str(exc)},
        )

    @app.exception_handler(ModelInferenceError)
    async def model_inference_exception_handler(request: Request, exc: ModelInferenceError):
        logger.error(f"Model inference error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "error": "ModelInferenceError", "detail": str(exc)},
        )

    # Register API v1 Routers
    api_v1_prefix = "/api/v1"
    app.include_router(customers_router, prefix=api_v1_prefix)
    app.include_router(segments_router, prefix=api_v1_prefix)
    app.include_router(analytics_router, prefix=api_v1_prefix)
    app.include_router(ml_router, prefix=api_v1_prefix)
    app.include_router(system_router, prefix=api_v1_prefix)

    @app.get("/", tags=["Root"])
    def api_root():
        return {
            "application": APP_NAME,
            "version": APP_VERSION,
            "status": "Operational 🟢",
            "documentation": "/api/docs",
            "endpoints": f"{api_v1_prefix}/...",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
