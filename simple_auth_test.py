import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.security import verify_password, create_access_token
from app.db.session import SessionLocal
from app.models.user import User
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_direct_auth():
    """直接認証機能をテスト"""
    try:
        # データベース接続テスト
        db = SessionLocal()
        
        # ユーザー検索
        user = db.query(User).filter(User.email == "user@example.com").first()
        if not user:
            logger.error("ユーザーが見つかりません")
            return False
        
        logger.info(f"ユーザーが見つかりました: {user.email}")
        logger.info(f"ハッシュされたパスワード: {user.hashed_password}")
        
        # パスワード検証
        password_valid = verify_password("string", user.hashed_password)
        logger.info(f"パスワード検証結果: {password_valid}")
        
        if password_valid:
            # トークン作成
            token = create_access_token({"sub": user.email})
            logger.info(f"トークン作成成功: {token[:50]}...")
            return True
        else:
            logger.error("パスワードが一致しません")
            return False
            
    except Exception as e:
        logger.error(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("直接認証テストを開始...")
    result = test_direct_auth()
    if result:
        print("✅ 認証機能は正常に動作しています")
    else:
        print("❌ 認証機能に問題があります")
