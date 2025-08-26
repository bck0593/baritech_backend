# Ashilog Backend API

## 概要
ペット管理アプリケーション「Ashilog」のバックエンドAPI

## 技術スタック
- **FastAPI** - 高速なWebフレームワーク
- **SQLAlchemy** - ORM（Object-Relational Mapping）
- **Azure Database for MySQL** - クラウドデータベース
- **JWT** - 認証システム
- **Alembic** - データベースマイグレーション

## 機能
- ユーザー認証・認可
- ペット情報管理
- 予約・スケジュール管理
- 健康記録管理
- 日記・食事記録
- 散歩・イベント管理
- コミュニティ機能

## セットアップ

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
```bash
cp .env
# .envファイルを編集して実際の値を設定
```

### 3. データベースマイグレーション
```bash
alembic upgrade head
```

### 4. アプリケーション起動
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## API ドキュメント
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## 環境変数
必要な環境変数を`.env`ファイルに設定してください：

### 必須設定
- `DATABASE_URL`: Azure MySQL接続文字列
- `JWT_SECRET`: JWT認証用シークレットキー
- `CORS_ORIGINS`: 許可するオリジン

### オプション設定
- `REDIS_HOST`: Redisホスト（キャッシュ用）
- `SMTP_HOST`: メールサーバーホスト

## データベース
Azure Database for MySQLを使用しています。SSL証明書（DigiCertGlobalRootCA.crt.pem）が必要です。

## 開発
```bash
# 開発サーバー起動
uvicorn app.main:app --reload

# テスト実行
pytest

# マイグレーション作成
alembic revision --autogenerate -m "description"
```

## 本番環境
本番環境では以下の設定を推奨します：
- `APP_ENV=production`
- `DEBUG=False`
- 適切なCORS設定
- SSL/TLS接続の強制

## ライセンス
MIT License
