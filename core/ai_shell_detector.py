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
        # Use a more robust pattern that handles nested brackets and newlines
        # Look for {"cmd": followed by balanced brackets
        start_pattern = r'\{"cmd"\s*:\s*\['
        
        # Find all potential start positions
        for match in re.finditer(start_pattern, response):
            start_pos = match.start()
            # Find the matching closing brace by counting brackets
            bracket_count = 0
            brace_count = 0
            in_string = False
            escape_next = False
            
            for i in range(start_pos, len(response)):
                char = response[i]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                    elif char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found the closing brace
                            json_str = response[start_pos:i+1]
                            try:
                                cmd_data = json.loads(json_str)
                                if 'cmd' in cmd_data and isinstance(cmd_data['cmd'], list):
                                    return cmd_data
                            except json.JSONDecodeError:
                                break
        
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

- User: "buat file hello_world.rs di /tmp"
  You: "I'll create a hello_world.rs file in /tmp directory.
  {"cmd":["bash","-lc","cat > /tmp/hello_world.rs << 'EOF'\nfn main() {\n    println!(\"Hello, world!\");\n}\nEOF\nls -l /tmp/hello_world.rs"]}"

- User: "berapa kapasitas disk, cpu, mem workstation ini?"
  You: "I'll check the disk, CPU, and memory information.
  {"cmd":["bash","-lc","echo 'Disk:' && df -h / && echo '' && echo 'CPU:' && sysctl -n machdep.cpu.brand_string && echo 'Cores:' && sysctl -n hw.ncpu && echo '' && echo 'Memory:' && vm_stat | head -5"]}"

- User: "buat 1000 temp file di /tmp lalu hapus"
  You: "I'll create 1000 temp files, benchmark the process, then clean up.
  {"cmd":["bash","-lc","START=$(python3 -c 'import time; print(int(time.time()*1000))') && for i in {1..1000}; do echo 'test' > /tmp/tmpfile_$i; done && END=$(python3 -c 'import time; print(int(time.time()*1000))') && echo \"Created 1000 files in $((END-START))ms\" && rm /tmp/tmpfile_* && echo 'Cleaned up'"]}"

Important:
- Safe read operations: ls, find, wc, cat, grep, pwd, df, du, top, ps, sysctl, vm_stat, etc.
- Safe write operations: ONLY to /tmp directory (echo >, cat >, touch, mkdir in /tmp)
- Safe cleanup: rm /tmp/tmpfile_* or rm /tmp/test_* (specific patterns in /tmp only)
- Never use rm -rf or rm without specific file patterns
- File creation/modification is ONLY allowed in /tmp directory
- For macOS: use sysctl for CPU info, vm_stat for memory, df for disk
- For macOS timing: use python3 -c 'import time; print(int(time.time()*1000))' (BSD date doesn't support %N)
- For Linux: use lscpu for CPU, free for memory, df for disk, date +%s%N for timing
- Always use the exact JSON format shown above
- Keep commands simple and focused on answering the user's question"""
