from typing import Tuple, List, Dict
from .session import SessionManager
from .shell_executor import ShellExecutor
from .ui import UI

class CommandHandler:
    """Handle interactive mode commands."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.ui = UI()
    
    def handle(self, cmd: str, history: List[Dict], model: str) -> Tuple[str, List[Dict]]:
        """
        Handle special commands.
        
        Returns:
            Tuple of (action, updated_history)
            action can be: 'continue', 'clear', 'exit', or None
        """
        cmd = cmd.strip()
        cmd_lower = cmd.lower()
        
        if cmd_lower == "/help":
            self.ui.print_help()
            return "continue", history
        
        elif cmd_lower == "/clear":
            self.ui.print_warning("Conversation history cleared.\n")
            return "clear", [{"role": "system", "content": "You are a helpful AI assistant."}]
        
        elif cmd_lower == "/resume":
            session = self.session_manager.load_session()
            if session and session.get("history"):
                self.ui.print_success(f"Resumed session from {session['timestamp']}\n")
                return "continue", session["history"]
            else:
                self.ui.print_warning("No previous session found.\n")
                return "continue", history
        
        elif cmd_lower.startswith("/shell "):
            command = cmd[7:].strip()
            if command:
                success, stdout, stderr = ShellExecutor.execute(command)
                ShellExecutor.display_result(success, stdout, stderr)
            else:
                self.ui.print_error("Usage: /shell <command>")
            return "continue", history
        
        elif cmd_lower in ["/exit", "/bye"]:
            return "exit", history
        
        return None, history
