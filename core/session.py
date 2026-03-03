import json
import datetime
from pathlib import Path
from typing import Optional, Dict, List
from .config import Config

class SessionManager:
    """Manage chat sessions and history."""
    
    def __init__(self):
        self.config = Config()
        self.session_file = self.config.get_session_dir() / "last_session.json"
    
    def save_session(self, history: List[Dict], model: str) -> None:
        """Save current session for resume."""
        session_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "history": history
        }
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
    
    def load_session(self) -> Optional[Dict]:
        """Load last session if exists."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None
    
    def save_chat_history(self, history: List[Dict], model: str) -> None:
        """Save chat history to memory/{date}.md"""
        if not history or len(history) <= 1:
            return
        
        memory_dir = self.config.get_memory_dir()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        file_path = memory_dir / f"{date_str}.md"
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Session: {time_str} (Model: {model})\n\n")
            for msg in history:
                if msg["role"] == "system":
                    continue
                role = "User" if msg["role"] == "user" else "Assistant"
                f.write(f"**{role}:**\n{msg['content']}\n\n")
