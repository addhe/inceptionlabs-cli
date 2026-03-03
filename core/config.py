import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for InceptionLabs CLI."""
    
    API_BASE_URL = "https://api.inceptionlabs.ai/v1"
    DEFAULT_CHAT_MODEL = "mercury-2"
    DEFAULT_EDIT_MODEL = "mercury-edit"
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_FIM_MAX_TOKENS = 512
    
    @staticmethod
    def get_api_key() -> str:
        """Get API key from environment."""
        return os.environ.get("INCEPTION_API_KEY", "")
    
    @staticmethod
    def get_session_dir() -> Path:
        """Get session directory path."""
        session_dir = Path.home() / ".inception" / "sessions"
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    @staticmethod
    def get_history_file() -> Path:
        """Get command history file path."""
        history_file = Path.home() / ".inception" / "history.txt"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        return history_file
    
    @staticmethod
    def get_memory_dir() -> Path:
        """Get memory directory for chat history."""
        memory_dir = Path("memory")
        memory_dir.mkdir(exist_ok=True)
        return memory_dir
