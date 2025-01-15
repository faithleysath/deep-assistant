import json
import sqlite3
from app.models import Message
from app.config import config

DB_PATH = config.get("DB_PATH")

def init_db():
    """初始化数据库连接并创建消息表。
    
    如果数据库文件不存在则创建，如果消息表已存在则先删除再创建。
    表结构包含以下字段：
        - id: 自增主键
        - message_id: 消息唯一标识
        - user_id: 用户ID
        - type: 消息类型
        - timestamp: 时间戳
        - raw_message: 原始消息内容
        - data: 附加数据
        
    示例：
        >>> init_db()  # 初始化数据库
    """
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # cursor.execute("DROP TABLE IF EXISTS messages")
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
    """将消息保存到数据库。
    
    Args:
        message_id (str): 消息唯一标识
        user_id (str): 发送消息的用户ID
        type (str): 消息类型
        timestamp (int): 消息时间戳
        raw_message (str): 原始消息内容
        data (str): 附加数据，通常为JSON格式
        
    Returns:
        None
        
    示例：
        >>> save_message("msg123", "user456", "text", 1698765432, "Hello", "{}")
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (message_id, user_id, type, timestamp, raw_message, data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (message_id, user_id, type, timestamp, raw_message, data))
        conn.commit()

def get_messages(limit: int = 100, uids: list[str] = None, types: list[str] = None) -> list[Message]:
    """从数据库获取消息记录。
    
    Args:
        limit (int): 返回消息数量限制，默认100
        uids (list[str]): 筛选指定用户ID列表，可选
        types (list[str]): 筛选指定消息类型列表，可选
        
    Returns:
        list[Message]: Message对象列表，包含解析后的消息数据
            
    Raises:
        sqlite3.Error: 如果数据库操作失败
        
    示例：
        >>> # 获取最近100条消息
        >>> messages = get_messages()
        >>> # 获取用户user123的最近50条消息
        >>> messages = get_messages(50, uids=["user123"])
        >>> # 获取类型为text的最近10条消息
        >>> messages = get_messages(10, types=["text"])
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
        messages = [Message.from_dict(json.loads(data)) for _, _, _, _, _, _, data in results]
        return messages

# 初始化数据库
init_db()
