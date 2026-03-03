import json
import re
from typing import Optional, Tuple
from .shell_executor import ShellExecutor
from .ui import UI

ui = UI()

class AIShellDetector:
    """Detect and extract shell commands from AI responses."""
    
    @staticmethod
    def extract_command(response: str) -> Optional[dict]:
        """
        Extract shell command from AI response.
        
        Expected format: {"cmd":["bash","-lc","command here"]}
        
        Returns:
            dict with 'cmd' key if found, None otherwise
        """
        # Try to find JSON command in response
        json_pattern = r'\{"cmd":\s*\[.*?\]\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            try:
                cmd_data = json.loads(matches[0])
                if 'cmd' in cmd_data and isinstance(cmd_data['cmd'], list):
                    return cmd_data
            except json.JSONDecodeError:
                pass
        
        return None
    
    @staticmethod
    def execute_from_response(response: str, auto_execute: bool = True) -> Tuple[str, bool]:
        """
        Extract and execute shell command from AI response.
        
        Args:
            response: AI response text
            auto_execute: Whether to auto-execute or just show command
            
        Returns:
            Tuple of (cleaned_response, command_executed)
        """
        cmd_data = AIShellDetector.extract_command(response)
        
        if not cmd_data:
            return response, False
        
        # Extract the actual command
        cmd_list = cmd_data['cmd']
        if len(cmd_list) >= 3 and cmd_list[0] == 'bash' and cmd_list[1] == '-lc':
            actual_command = cmd_list[2]
        else:
            actual_command = ' '.join(cmd_list)
        
        # Remove the JSON command from response
        cleaned_response = re.sub(r'\{"cmd":\s*\[.*?\]\}', '', response, flags=re.DOTALL).strip()
        
        # Show what command will be executed
        ui.print_info(f"\n🔧 Detected command: [bold cyan]{actual_command}[/bold cyan]")
        
        if auto_execute:
            # Execute the command
            success, stdout, stderr = ShellExecutor.execute(actual_command)
            ShellExecutor.display_result(success, stdout, stderr)
            return cleaned_response, True
        else:
            ui.print_warning("Auto-execution disabled. Use /shell to run manually.")
            return cleaned_response, False
    
    @staticmethod
    def create_system_prompt() -> str:
        """Create system prompt that instructs AI to generate shell commands."""
        return """You are a helpful AI assistant with shell command execution capabilities.

When a user asks a question that requires checking the system or file system, you should:
1. Provide a brief explanation of what you'll do
2. Generate a shell command in this exact JSON format: {"cmd":["bash","-lc","your command here"]}
3. The command will be automatically executed and results shown to the user

Examples:
- User: "ada berapa file di /tmp ?"
  You: "I'll check the number of files in /tmp directory.
  {"cmd":["bash","-lc","find /tmp -maxdepth 1 -type f | wc -l"]}"

- User: "ada berapa folder dan files di directory ini ?"
  You: "Let me count the folders and files in the current directory.
  {"cmd":["bash","-lc","echo 'Folders:' && find . -maxdepth 1 -type d | wc -l && echo 'Files:' && find . -maxdepth 1 -type f | wc -l"]}"

Important:
- Only generate commands for safe, read-only operations (ls, find, wc, cat, grep, etc.)
- Never generate destructive commands (rm, mv, chmod, etc.)
- Always use the exact JSON format shown above
- Keep commands simple and focused on answering the user's question"""
