from typing import Tuple, List, Dict, Optional
from .session import SessionManager
from .shell_executor import ShellExecutor
from .ui import UI

class CommandHandler:
    """Handle interactive mode commands."""
    
    def __init__(self, session_manager: SessionManager, skill_manager=None):
        self.session_manager = session_manager
        self.skill_manager = skill_manager
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
        
        elif cmd_lower == "/skills":
            if self.skill_manager:
                self._show_skills()
            else:
                self.ui.print_warning("Skills system not initialized")
            return "continue", history
        
        elif cmd_lower in ["/exit", "/bye"]:
            return "exit", history
        
        return None, history
    
    def _show_skills(self) -> None:
        """Display available skills."""
        from rich.table import Table
        from rich.console import Console
        
        console = Console()
        skills = self.skill_manager.list_skills()
        
        if not skills:
            self.ui.print_warning("No skills available. Add skill files to the 'skills/' directory.")
            return
        
        table = Table(title="Available Skills")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="green")
        table.add_column("Description", style="white")
        
        for skill_meta in skills:
            table.add_row(
                skill_meta.name,
                skill_meta.version,
                skill_meta.description
            )
        
        console.print(table)
        console.print("\n[bold]Usage:[/bold] Ask the AI to use a skill naturally, e.g.:")
        console.print("  • 'analyze the cli.py file'")
        console.print("  • 'search the web for Python best practices'")
        console.print("  • 'show me the git log'")
        console.print("\nOr use JSON format directly:")
        console.print('  {"skill": "file_analyzer", "params": {"path": "cli.py"}}')
