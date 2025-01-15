import os
from pathlib import Path
from typing import Optional

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "database.db"))

# WebSocket configuration
WEBSOCKET_URI = os.getenv("WEBSOCKET_URI", "ws://localhost:8080/ws")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))

class Config:
    def __init__(self):
        self.database_path = DATABASE_PATH
        self.websocket_uri = WEBSOCKET_URI
        self.log_level = LOG_LEVEL
        self.log_file = LOG_FILE

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path}"

    def validate(self) -> bool:
        """Validate configuration values"""
        required_dirs = [
            Path(self.database_path).parent,
            Path(self.log_file).parent
        ]
        
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        return all([
            self.websocket_uri.startswith(("ws://", "wss://")),
            self.log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        ])
