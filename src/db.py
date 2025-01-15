import sqlite3
from pathlib import Path
from .models import Message

DB_PATH = "messages.db"

def init_db():
    """初始化数据库"""
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS messages")
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

def get_messages(limit: int = 100, uids: list[str] = None, types: list[str] = None) -> list[tuple[int, str, str, str, int, str, str]]:
    """获取最近的消息
    Args:
        limit: 返回消息数量限制
        uids: 筛选指定用户ID列表
        types: 筛选指定消息类型列表
    Returns:
        list[tuple[int, str, str, str, int, str, str]]: 包含消息记录的元组列表，每个元组包含：
            - id: int 消息ID
            - message_id: str 消息唯一标识
            - user_id: str 用户ID
            - type: str 消息类型
            - timestamp: int 时间戳
            - raw_message: str 原始消息内容
            - data: str 附加数据
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        query = "SELECT * FROM messages"
        params = []
        
        # 构建WHERE条件
        conditions = []
        if uids:
            conditions.append(f"user_id IN ({','.join(['?']*len(uids))})")
            params.extend(uids)
        if types:
            conditions.append(f"type IN ({','.join(['?']*len(types))})")
            params.extend(types)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        messages = [Message.from_dict(data) for _, _, _, _, _, _, data in results]
        return messages

# 初始化数据库
init_db()
