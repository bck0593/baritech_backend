import traceback
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# 直接パスワード検証テスト
def test_password_verification():
    try:
        # bcryptを直接インポートしてテスト
        import bcrypt
        print(f"✅ bcrypt version: {bcrypt.__version__}")
        
        # ユーザーのハッシュ化パスワードを取得
        with engine.connect() as connection:
            result = connection.execute(text("SELECT hashed_password FROM ユーザー WHERE email = 'user@example.com'"))
            user_data = result.fetchone()
            
            if user_data:
                stored_hash = user_data[0]
                print(f"🔍 Stored hash: {stored_hash[:50]}...")
                
                # 様々なパスワードでテスト
                test_passwords = ["string", "password", "password123"]
                
                for pwd in test_passwords:
                    try:
                        # bcryptで直接検証
                        is_valid = bcrypt.checkpw(pwd.encode('utf-8'), stored_hash.encode('utf-8'))
                        print(f"  bcrypt.checkpw('{pwd}'): {is_valid}")
                        
                        # passlib経由でも検証
                        from passlib.context import CryptContext
                        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                        is_valid_passlib = pwd_context.verify(pwd, stored_hash)
                        print(f"  passlib.verify('{pwd}'): {is_valid_passlib}")
                        
                    except Exception as e:
                        print(f"  ❌ Error testing '{pwd}': {e}")
                        traceback.print_exc()
            else:
                print("❌ ユーザーが見つかりません")
                
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        traceback.print_exc()

# FastAPIで使用されているverify_password関数をテスト
def test_verify_password_function():
    try:
        # FastAPIのverify_password関数を直接インポート
        from app.core.security import verify_password
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT hashed_password FROM ユーザー WHERE email = 'user@example.com'"))
            user_data = result.fetchone()
            
            if user_data:
                stored_hash = user_data[0]
                print(f"\n🔍 FastAPI verify_password テスト:")
                
                test_passwords = ["string", "password", "password123"]
                for pwd in test_passwords:
                    try:
                        is_valid = verify_password(pwd, stored_hash)
                        print(f"  verify_password('{pwd}'): {is_valid}")
                    except Exception as e:
                        print(f"  ❌ Error in verify_password('{pwd}'): {e}")
                        traceback.print_exc()
                        
    except Exception as e:
        print(f"❌ FastAPI function test error: {e}")
        traceback.print_exc()

# ログインエンドポイントを直接テスト
def test_login_endpoint():
    try:
        from app.api.v1.routers.auth import login_user
        from app.schemas.user import UserLogin
        from app.db.session import SessionLocal
        
        print(f"\n🔍 FastAPI login endpoint テスト:")
        
        # データベースセッションを作成
        db = SessionLocal()
        
        # UserLoginオブジェクトを作成
        user_login = UserLogin(email="user@example.com", password="string")
        
        try:
            # ログイン関数を直接呼び出し
            result = login_user(user_login, db)
            print(f"  ✅ Login successful: {result}")
        except Exception as e:
            print(f"  ❌ Login failed: {e}")
            traceback.print_exc()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Login endpoint test error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 FastAPI認証エラー詳細調査")
    print("=" * 60)
    
    test_password_verification()
    test_verify_password_function()
    test_login_endpoint()
