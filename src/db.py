import sqlite3
from pathlib import Path
import time

DB_PATH = "messages.db"

def init_db():
    """初始化数据库"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                raw_message TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        conn.commit()

def save_message(message_id: str, user_id: str, type: str, timestamp: int, raw_message: str, data: str):
    """保存消息到数据库"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (message_id, user_id, type, timestamp, raw_message, data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, user_id, type, timestamp, raw_message, data))
        conn.commit()

def get_messages(limit: int = 100):
    """获取最近的消息"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages
            ORDER BY timestamp ASC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

# 初始化数据库
init_db()
