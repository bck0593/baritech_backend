"""
Azure FastAPI メインアプリケーション
====================================
CORS設定を統合したFastAPIアプリケーションの実装例
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import os
import logging
from typing import Optional, Dict, Any

# CORS設定をインポート
from cors_middleware import configure_cors_for_azure, AzureAppServiceCORSConfig

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPIアプリの初期化
app = FastAPI(
    title="Baritech API",
    description="Dog Daycare Management System",
    version="0.1.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT", "development") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "development") != "production" else None,
)

# Azure用CORS設定の適用
configure_cors_for_azure(
    app=app,
    enable_security_headers=True,
    enable_preflight_optimization=True
)

# 認証設定
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """JWT認証の実装（簡略化）"""
    # 実際の実装では、JWTトークンの検証を行う
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # トークン検証ロジック（実装により異なる）
    # decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
    return {"user_id": "test_user", "email": "user@example.com"}

# ヘルスチェックエンドポイント
@app.get("/healthz")
@app.get("/health")
async def health_check():
    """
    Azure App Service のヘルスチェック
    """
    return {
        "status": "healthy",
        "service": "baritech-api",
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "cors_enabled": True,
        "timestamp": "2025-01-20T12:00:00Z"
    }

# CORS テスト用エンドポイント
@app.get("/api/v1/cors-test")
async def cors_test():
    """CORS設定のテスト用エンドポイント"""
    config = AzureAppServiceCORSConfig()
    
    return {
        "message": "CORS test successful",
        "environment": config.environment,
        "allowed_origins": config.allowed_origins,
        "cors_working": True
    }

# 認証エンドポイント
@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """
    ユーザー認証エンドポイント
    """
    email = credentials.get("email")
    password = credentials.get("password")
    
    # 簡単な認証チェック（実際の実装では適切な認証を行う）
    if email == "user@example.com" and password == "string":
        return {
            "access_token": "test_jwt_token_here",
            "refresh_token": "test_refresh_token_here",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": "user123",
                "email": email,
                "name": "Test User",
                "role": "user"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/v1/auth/me")
async def get_current_user_info(user = Depends(get_current_user)):
    """
    現在のユーザー情報取得
    """
    return {
        "id": "user123",
        "email": "user@example.com",
        "name": "Test User",
        "role": "user",
        "avatar": None
    }

# 予約関連エンドポイント
@app.get("/api/v1/bookings/")
async def get_bookings(user = Depends(get_current_user)):
    """
    予約一覧取得
    """
    return [
        {
            "id": "booking1",
            "service_type": "デイケア",
            "booking_date": "2025-01-21",
            "status": "confirmed",
            "dog_id": "dog1"
        },
        {
            "id": "booking2",
            "service_type": "お散歩",
            "booking_date": "2025-01-22",
            "status": "pending",
            "dog_id": "dog2"
        }
    ]

@app.post("/api/v1/bookings/")
async def create_booking(booking_data: dict, user = Depends(get_current_user)):
    """
    新規予約作成
    """
    return {
        "id": "new_booking_id",
        "message": "Booking created successfully",
        **booking_data
    }

# 犬情報エンドポイント
@app.get("/api/v1/dogs/")
async def get_dogs(user = Depends(get_current_user)):
    """
    犬一覧取得
    """
    return [
        {
            "id": "dog1",
            "name": "ポチ",
            "breed": "柴犬",
            "age": 3,
            "owner_id": "user123"
        },
        {
            "id": "dog2",
            "name": "ハナ",
            "breed": "トイプードル",
            "age": 2,
            "owner_id": "user123"
        }
    ]

# エラーハンドリング
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    HTTPエラーの統一ハンドリング
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# アプリケーション起動時の設定
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    logger.info("Starting Baritech API...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info("CORS configuration applied successfully")
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("Shutting down Baritech API...")

if __name__ == "__main__":
    import uvicorn
    
    # 開発環境での実行
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
