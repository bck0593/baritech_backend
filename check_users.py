import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("🔍 ユーザーテーブルの詳細情報:")
        print("=" * 50)
        
        # ユーザー一覧を表示
        result = connection.execute(text("SELECT id, name, email, status, role FROM ユーザー ORDER BY created_at"))
        users = result.fetchall()
        
        print(f"\n📋 登録ユーザー一覧 ({len(users)}人):")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user[1]} ({user[2]}) - {user[3]} - {user[4]}")
        
        # user@example.com に近いメールアドレスを検索
        print(f"\n🔍 'example.com' を含むユーザー:")
        result = connection.execute(text("SELECT id, name, email, status, role FROM ユーザー WHERE email LIKE '%example.com%'"))
        example_users = result.fetchall()
        
        if example_users:
            for user in example_users:
                print(f"  ✅ {user[1]} ({user[2]}) - {user[3]} - {user[4]}")
        else:
            print("  ❌ example.com ドメインのユーザーは見つかりませんでした")
        
        # ハッシュ化されたパスワードの状況を確認
        print(f"\n🔒 パスワード設定状況:")
        result = connection.execute(text("SELECT name, email, CASE WHEN hashed_password IS NULL THEN 'NULL' WHEN hashed_password = '' THEN '空文字' ELSE '設定済み' END as password_status FROM ユーザー ORDER BY name"))
        password_status = result.fetchall()
        
        for user in password_status:
            print(f"  {user[0]} ({user[1]}): {user[2]}")
        
        # 'tanaka@example.com' のユーザーをチェック
        print(f"\n🔍 tanaka@example.com ユーザー詳細:")
        result = connection.execute(text("SELECT * FROM ユーザー WHERE email = 'tanaka@example.com'"))
        tanaka_user = result.fetchone()
        
        if tanaka_user:
            print(f"  ✅ 見つかりました:")
            print(f"    ID: {tanaka_user[0]}")
            print(f"    名前: {tanaka_user[1]}")
            print(f"    メール: {tanaka_user[2]}")
            print(f"    ステータス: {tanaka_user[3]}")
            print(f"    ロール: {tanaka_user[4]}")
            print(f"    パスワード: {'設定済み' if tanaka_user[7] else '未設定'}")
        else:
            print("  ❌ tanaka@example.com のユーザーは見つかりませんでした")
        
        # APIで使えそうなテストユーザーを探す
        print(f"\n🧪 テスト用ユーザー候補:")
        result = connection.execute(text("SELECT name, email, status, role FROM ユーザー WHERE status = '有効' AND hashed_password IS NOT NULL AND hashed_password != '' ORDER BY created_at LIMIT 5"))
        test_users = result.fetchall()
        
        for i, user in enumerate(test_users, 1):
            print(f"  {i}. {user[0]} ({user[1]}) - {user[2]} - {user[3]}")

except Exception as e:
    print(f"❌ エラー: {e}")
