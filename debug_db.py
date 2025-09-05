import os
import traceback
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

# .envファイルを読み込み
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

try:
    print("=== URL解析テスト ===")
    url = make_url(DATABASE_URL)
    print(f"URL作成成功: {url}")
    print(f"Backend: {url.get_backend_name()}")
    print(f"Driver: {url.get_driver_name()}")
    print(f"Host: {url.host}")
    print(f"Port: {url.port}")
    print(f"Database: {url.database}")
    print(f"Username: {url.username}")
    
except Exception as e:
    print(f"URL解析エラー: {e}")
    traceback.print_exc()

try:
    print("\n=== エンジン作成テスト ===")
    engine = create_engine(DATABASE_URL, echo=True)
    print("エンジン作成成功")
    
    print("\n=== 接続テスト ===")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 AS test"))
        print(f"接続成功: {result.fetchone()}")
        
except Exception as e:
    print(f"データベース接続エラー: {e}")
    traceback.print_exc()
