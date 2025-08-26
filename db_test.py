# db_test.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# データベース接続
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    """データベース接続をテスト"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ データベース接続成功")
            return True
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return False

def show_tables():
    """テーブル一覧を表示"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 テーブル一覧 ({len(tables)}個):")
            for table in tables:
                print(f"  - {table}")
            return tables
    except Exception as e:
        print(f"❌ テーブル一覧取得エラー: {e}")
        return []

def show_table_structure(table_name):
    """指定したテーブルの構造を表示"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"DESCRIBE {table_name}"))
            columns = result.fetchall()
            print(f"\n📊 テーブル構造: {table_name}")
            print("  Field\t\tType\t\tNull\tKey\tDefault\tExtra")
            print("  " + "-" * 80)
            for col in columns:
                print(f"  {col[0]}\t\t{col[1]}\t\t{col[2]}\t{col[3]}\t{col[4]}\t{col[5]}")
    except Exception as e:
        print(f"❌ テーブル構造取得エラー: {e}")

def count_records(table_name):
    """指定したテーブルのレコード数を表示"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.fetchone()[0]
            print(f"  📊 {table_name}: {count}件")
            return count
    except Exception as e:
        print(f"❌ レコード数取得エラー: {e}")
        return 0

def show_sample_data(table_name, limit=5):
    """指定したテーブルのサンプルデータを表示"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
            rows = result.fetchall()
            if rows:
                print(f"\n📄 サンプルデータ: {table_name}")
                for i, row in enumerate(rows, 1):
                    print(f"  {i}: {row}")
            else:
                print(f"  📄 {table_name}: データなし")
    except Exception as e:
        print(f"❌ サンプルデータ取得エラー: {e}")

if __name__ == "__main__":
    print("🔍 Azure MySQLデータベース確認ツール")
    print("=" * 50)
    
    # 接続テスト
    if test_connection():
        # テーブル一覧表示
        tables = show_tables()
        
        if tables:
            # 各テーブルのレコード数を表示
            print(f"\n📈 レコード数:")
            for table in tables:
                count_records(table)
            
            # 主要テーブルの構造を表示
            main_tables = ['users', 'owners', 'dogs', 'bookings', 'posts']
            for table in main_tables:
                if table in tables:
                    show_table_structure(table)
                    show_sample_data(table)

                    # ... existing code ...

def show_user_data():
    """ユーザーテーブルの詳細データを表示"""
    try:
        with engine.connect() as connection:
            # テーブル構造を表示
            print("\n📊 ユーザーテーブル構造:")
            result = connection.execute(text("DESCRIBE ユーザー"))
            columns = result.fetchall()
            print("  Field\t\tType\t\tNull\tKey\tDefault\tExtra")
            print("  " + "-" * 80)
            for col in columns:
                print(f"  {col[0]}\t\t{col[1]}\t\t{col[2]}\t{col[3]}\t{col[4]}\t{col[5]}")
            
            # 全ユーザーデータを表示
            print(f"\n�� ユーザーデータ (全18件):")
            result = connection.execute(text("SELECT * FROM ユーザー ORDER BY id"))
            rows = result.fetchall()
            
            for i, row in enumerate(rows, 1):
                print(f"\n  📋 ユーザー {i}:")
                print(f"    ID: {row[0]}")
                print(f"    メールアドレス: {row[1]}")
                print(f"    ユーザー名: {row[2]}")
                print(f"    フルネーム: {row[3]}")
                print(f"    電話番号: {row[4]}")
                print(f"    住所: {row[5]}")
                print(f"    生年月日: {row[6]}")
                print(f"    性別: {row[7]}")
                print(f"    プロフィール画像: {row[8]}")
                print(f"    自己紹介: {row[9]}")
                print(f"    ステータス: {row[10]}")
                print(f"    ロール: {row[11]}")
                print(f"    作成日時: {row[12]}")
                print(f"    更新日時: {row[13]}")
                
    except Exception as e:
        print(f"❌ ユーザーデータ取得エラー: {e}")

def show_user_summary():
    """ユーザーの統計情報を表示"""
    try:
        with engine.connect() as connection:
            print("\n📈 ユーザー統計情報:")
            
            # ステータス別ユーザー数
            result = connection.execute(text("SELECT ステータス, COUNT(*) FROM ユーザー GROUP BY ステータス"))
            status_counts = result.fetchall()
            print("  📊 ステータス別ユーザー数:")
            for status, count in status_counts:
                print(f"    {status}: {count}人")
            
            # ロール別ユーザー数
            result = connection.execute(text("SELECT ロール, COUNT(*) FROM ユーザー GROUP BY ロール"))
            role_counts = result.fetchall()
            print("  📊 ロール別ユーザー数:")
            for role, count in role_counts:
                print(f"    {role}: {count}人")
            
            # 性別別ユーザー数
            result = connection.execute(text("SELECT 性別, COUNT(*) FROM ユーザー GROUP BY 性別"))
            gender_counts = result.fetchall()
            print("  📊 性別別ユーザー数:")
            for gender, count in gender_counts:
                print(f"    {gender}: {count}人")
                
    except Exception as e:
        print(f"❌ ユーザー統計情報取得エラー: {e}")

def show_vaccination_data():
    """予防接種テーブルの詳細データを表示"""
    try:
        with engine.connect() as connection:
            # テーブル構造を表示
            print("\n📊 予防接種テーブル構造:")
            result = connection.execute(text("DESCRIBE 予防接種"))
            columns = result.fetchall()
            print("  Field\t\tType\t\tNull\tKey\tDefault\tExtra")
            print("  " + "-" * 80)
            for col in columns:
                print(f"  {col[0]}\t\t{col[1]}\t\t{col[2]}\t{col[3]}\t{col[4]}\t{col[5]}")
            
            # 全予防接種データを表示
            print(f"\n💉 予防接種データ:")
            result = connection.execute(text("SELECT * FROM 予防接種 ORDER BY id"))
            rows = result.fetchall()
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\n  📋 予防接種記録 {i}:")
                    print(f"    ID: {row[0]}")
                    print(f"    犬ID: {row[1]}")
                    print(f"    ワクチン名: {row[2]}")
                    print(f"    接種日: {row[3]}")
                    print(f"    次回接種予定日: {row[4]}")
                    print(f"    獣医師名: {row[5]}")
                    print(f"    ロット番号: {row[6]}")
                    print(f"    備考: {row[7]}")
                    print(f"    作成日時: {row[8]}")
            else:
                print("  📄 予防接種データ: データなし")
                
    except Exception as e:
        print(f"❌ 予防接種データ取得エラー: {e}")

def show_vaccination_summary():
    """予防接種の統計情報を表示"""
    try:
        with engine.connect() as connection:
            print("\n📈 予防接種統計情報:")
            
            # 全件数
            result = connection.execute(text("SELECT COUNT(*) FROM 予防接種"))
            total_count = result.fetchone()[0]
            print(f"  📊 総予防接種記録数: {total_count}件")
            
            # ワクチン名別件数
            result = connection.execute(text("SELECT vaccine_name, COUNT(*) FROM 予防接種 GROUP BY vaccine_name"))
            vaccine_counts = result.fetchall()
            print("  📊 ワクチン名別件数:")
            for vaccine, count in vaccine_counts:
                print(f"    {vaccine}: {count}件")
            
            # 犬別件数
            result = connection.execute(text("SELECT d.name, COUNT(v.id) FROM 予防接種 v JOIN 犬 d ON v.dog_id = d.id GROUP BY v.dog_id, d.name"))
            dog_counts = result.fetchall()
            print("  📊 犬別予防接種件数:")
            for dog_name, count in dog_counts:
                print(f"    {dog_name}: {count}件")
            
            # 月別件数（今年）
            result = connection.execute(text("SELECT MONTH(administered_on) as month, COUNT(*) FROM 予防接種 WHERE YEAR(administered_on) = YEAR(CURDATE()) GROUP BY MONTH(administered_on) ORDER BY month"))
            monthly_counts = result.fetchall()
            print("  📊 今年の月別予防接種件数:")
            for month, count in monthly_counts:
                month_name = ["", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"][month]
                print(f"    {month_name}: {count}件")
                
    except Exception as e:
        print(f"❌ 予防接種統計情報取得エラー: {e}")

def show_upcoming_vaccinations():
    """今後の予防接種予定を表示"""
    try:
        with engine.connect() as connection:
            print("\n📅 今後の予防接種予定:")
            
            # 30日以内の予防接種予定
            result = connection.execute(text("""
                SELECT v.id, d.name as dog_name, v.vaccine_name, v.next_due_on, 
                       DATEDIFF(v.next_due_on, CURDATE()) as days_until
                FROM 予防接種 v 
                JOIN 犬 d ON v.dog_id = d.id 
                WHERE v.next_due_on >= CURDATE() 
                ORDER BY v.next_due_on
            """))
            upcoming = result.fetchall()
            
            if upcoming:
                for row in upcoming:
                    days_until = row[4]
                    if days_until == 0:
                        status = "🟡 今日"
                    elif days_until <= 7:
                        status = "🔴 1週間以内"
                    elif days_until <= 30:
                        status = "🟠 1ヶ月以内"
                    else:
                        status = "🟢 1ヶ月以上先"
                    
                    print(f"  {status} {row[2]} ({row[1]}): {row[3]} (あと{days_until}日)")
            else:
                print("  📄 今後の予防接種予定: なし")
                
    except Exception as e:
        print(f"❌ 予防接種予定取得エラー: {e}")

def show_all_tables_detailed():
    """全テーブルの詳細情報を表示"""
    try:
        with engine.connect() as connection:
            # 全テーブル一覧
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 全テーブル詳細情報 ({len(tables)}個):")
            for i, table in enumerate(tables, 1):
                # テーブル構造
                result = connection.execute(text(f"DESCRIBE {table}"))
                columns = result.fetchall()
                
                # レコード数
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                
                print(f"\n  📊 {i}. {table}:")
                print(f"    レコード数: {count}件")
                print(f"    カラム数: {len(columns)}個")
                print(f"    カラム: {[col[0] for col in columns]}")
                
                # データが存在する場合はサンプルデータも表示
                if count > 0:
                    try:
                        result = connection.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                        sample = result.fetchone()
                        if sample:
                            print(f"    サンプル: {dict(zip([col[0] for col in columns], sample))}")
                    except:
                        print(f"    サンプル: 取得不可")
                else:
                    print(f"    サンプル: データなし")
                
            return tables
    except Exception as e:
        print(f"❌ テーブル詳細情報取得エラー: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Azure MySQLデータベース構造詳細確認ツール")
    print("=" * 60)
    
    # 接続テスト
    if test_connection():
        # 全テーブルの詳細情報表示
        tables = show_all_tables_detailed()
        
        # 主要統計情報
        print(f"\n📈 データベース統計:")
        print(f"  総テーブル数: {len(tables)}個")
        
        # データが存在するテーブルとしないテーブルを分類
        if tables:
            with engine.connect() as connection:
                empty_tables = []
                data_tables = []
                
                for table in tables:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    if count == 0:
                        empty_tables.append(table)
                    else:
                        data_tables.append((table, count))
                
                print(f"  データ有りテーブル: {len(data_tables)}個")
                for table, count in data_tables:
                    print(f"    - {table}: {count}件")
                
                print(f"  データ無しテーブル: {len(empty_tables)}個")
                for table in empty_tables:
                    print(f"    - {table}")
    
    print("\n" + "=" * 60)