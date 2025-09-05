from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.api import api_router
import logging
import traceback

# ログ設定を詳細に
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

logger.info("FastAPI application initialized")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = traceback.format_exc()
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Full traceback: {error_detail}")
    logger.error(f"Request URL: {request.url}")
    logger.error(f"Request method: {request.method}")
    
    # リクエストボディを安全に読み取り
    try:
        body = await request.body()
        logger.error(f"Request body: {body}")
    except Exception as body_err:
        logger.error(f"Could not read request body: {body_err}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

# 開発環境用の柔軟なCORS設定
# if settings.APP_ENV == "dev":
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],  # 開発環境では全てのオリジンを許可
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
# else:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.cors_origins_list,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

# 問題調査のためCORSを一時的に無効化

app.include_router(api_router, prefix="/api/v1")
logger.info("API router included")


@app.get("/healthz")
def healthz():
    logger.info("Health check endpoint called")
    return {"status": "ok"}
