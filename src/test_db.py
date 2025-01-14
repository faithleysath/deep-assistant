import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "messages.db"

def test_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("数据库中的表：", tables)
            
            cursor.execute("SELECT * FROM messages LIMIT 5")
            messages = cursor.fetchall()
            print("最近5条消息：", messages)
            
    except Exception as e:
        print("数据库测试失败：", str(e))

if __name__ == "__main__":
    test_db()
