"""
Azure FastAPI CORS設定ミドルウェア
=====================================
Next.js フロントエンド (localhost:3000) から
Azure App Service FastAPI への接続最適化
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from typing import List, Optional
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedCORSConfig:
    """最適化されたCORS設定クラス"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        
    @property
    def allowed_origins(self) -> List[str]:
        """許可するオリジンを環境に応じて設定"""
        if self.is_production:
            # 本番環境: 特定ドメインのみ
            return [
                "https://your-production-domain.com",
                "https://www.your-production-domain.com",
                # Azure Static Web Apps の場合
                "https://*.azurestaticapps.net",
                # カスタムドメインがある場合は追加
            ]
        else:
            # 開発環境: ローカル開発用
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",  # 代替ポート
                "https://localhost:3000",  # HTTPS対応
                # Vercel Preview環境
                "https://*.vercel.app",
                # その他の開発環境
                "http://192.168.*:3000",  # ローカルネットワーク
            ]
    
    @property
    def allowed_methods(self) -> List[str]:
        """許可するHTTPメソッド"""
        return [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
            "HEAD",
        ]
    
    @property
    def allowed_headers(self) -> List[str]:
        """許可するヘッダー"""
        return [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "X-Client-Version",
            "User-Agent",
            "Cache-Control",
            "Pragma",
        ]
    
    @property
    def expose_headers(self) -> List[str]:
        """フロントエンドに公開するヘッダー"""
        return [
            "X-Total-Count",
            "X-Page-Count",
            "X-Per-Page",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
            "Content-Disposition",
        ]

def setup_cors_middleware(app: FastAPI, config: Optional[OptimizedCORSConfig] = None) -> None:
    """
    FastAPIアプリにCORSミドルウェアを設定
    
    Args:
        app: FastAPIアプリインスタンス
        config: CORS設定（オプション）
    """
    if config is None:
        config = OptimizedCORSConfig()
    
    logger.info(f"Setting up CORS for environment: {config.environment}")
    logger.info(f"Allowed origins: {config.allowed_origins}")
    
    # CORSミドルウェアの追加
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=config.allowed_methods,
        allow_headers=config.allowed_headers,
        expose_headers=config.expose_headers,
        max_age=86400,  # プリフライトリクエストのキャッシュ時間（24時間）
    )
    
    # 信頼できるホストの設定（セキュリティ強化）
    if config.is_production:
        trusted_hosts = [
            "*.azurewebsites.net",
            "your-production-domain.com",
            "www.your-production-domain.com",
        ]
        
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )
        
        logger.info(f"Trusted hosts configured: {trusted_hosts}")

# 環境変数ベースの詳細設定
class EnvironmentBasedCORSConfig(OptimizedCORSConfig):
    """環境変数ベースのCORS設定"""
    
    def __init__(self):
        super().__init__()
        
        # 環境変数から追加オリジンを読み取り
        additional_origins = os.getenv("CORS_ADDITIONAL_ORIGINS", "")
        self.additional_origins = [
            origin.strip() 
            for origin in additional_origins.split(",") 
            if origin.strip()
        ]
    
    @property
    def allowed_origins(self) -> List[str]:
        """環境変数を考慮したオリジン設定"""
        base_origins = super().allowed_origins
        return base_origins + self.additional_origins

# Azure App Service 特化設定
class AzureAppServiceCORSConfig(EnvironmentBasedCORSConfig):
    """Azure App Service専用CORS設定"""
    
    @property
    def allowed_origins(self) -> List[str]:
        base_origins = super().allowed_origins
        
        # Azure App Service の場合の追加設定
        azure_origins = []
        
        if self.is_production:
            # 本番Azure App Service
            azure_origins.extend([
                "https://*.azurewebsites.net",
                "https://*.azurestaticapps.net",
                # Application Gateway経由の場合
                "https://*.cloudapp.azure.com",
            ])
        else:
            # 開発・ステージング環境
            azure_origins.extend([
                # ローカル開発環境
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                # Azure Preview環境
                "https://*-preview.azurewebsites.net",
                "https://*-staging.azurewebsites.net",
            ])
        
        return base_origins + azure_origins

# プリフライトリクエスト最適化
def add_preflight_optimization(app: FastAPI) -> None:
    """プリフライトリクエストの最適化"""
    
    @app.options("/{path:path}")
    async def preflight_handler(path: str):
        """プリフライトリクエストの高速処理"""
        return {
            "status": "ok",
            "path": path,
            "timestamp": "2025-01-20T12:00:00Z"
        }

# セキュリティヘッダーの追加
def add_security_headers(app: FastAPI) -> None:
    """セキュリティヘッダーの追加"""
    
    @app.middleware("http")
    async def add_security_headers_middleware(request, call_next):
        response = await call_next(request)
        
        # セキュリティヘッダーを追加
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self' https:; "
                "object-src 'none'; "
                "media-src 'self'; "
                "frame-src 'none';"
            ),
        })
        
        return response

# 統合設定関数
def configure_cors_for_azure(
    app: FastAPI, 
    enable_security_headers: bool = True,
    enable_preflight_optimization: bool = True,
    custom_config: Optional[OptimizedCORSConfig] = None
) -> None:
    """
    Azure App Service向けの完全CORS設定
    
    Args:
        app: FastAPIアプリインスタンス
        enable_security_headers: セキュリティヘッダーの有効化
        enable_preflight_optimization: プリフライト最適化の有効化
        custom_config: カスタムCORS設定
    
    Example:
        ```python
        from fastapi import FastAPI
        from cors_middleware import configure_cors_for_azure
        
        app = FastAPI()
        configure_cors_for_azure(app)
        ```
    """
    
    # CORS設定
    config = custom_config or AzureAppServiceCORSConfig()
    setup_cors_middleware(app, config)
    
    # セキュリティヘッダー
    if enable_security_headers:
        add_security_headers(app)
        logger.info("Security headers enabled")
    
    # プリフライト最適化
    if enable_preflight_optimization:
        add_preflight_optimization(app)
        logger.info("Preflight optimization enabled")
    
    logger.info("Azure CORS configuration completed successfully")

# 使用例とテスト関数
def test_cors_configuration() -> dict:
    """CORS設定のテスト"""
    config = AzureAppServiceCORSConfig()
    
    return {
        "environment": config.environment,
        "is_production": config.is_production,
        "allowed_origins": config.allowed_origins,
        "allowed_methods": config.allowed_methods,
        "allowed_headers": config.allowed_headers[:5],  # 最初の5つのみ表示
        "total_headers": len(config.allowed_headers),
    }

if __name__ == "__main__":
    # 設定テスト
    test_result = test_cors_configuration()
    print("CORS Configuration Test:")
    for key, value in test_result.items():
        print(f"  {key}: {value}")
