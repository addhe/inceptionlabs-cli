import subprocess
import shlex
from typing import Tuple
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class ShellExecutor:
    """Execute shell commands safely."""
    
    DANGEROUS_COMMANDS = [
        'rm -rf', 'rmdir', 'del', 'format', 'mkfs',
        'dd', 'shutdown', 'reboot', 'halt',
        'sudo', 'su', 'chmod 777', 'chown'
    ]
    
    SAFE_WRITE_PATTERNS = [
        r'cat\s+<<.*?>\s+/tmp/',  # heredoc to /tmp
        r'echo\s+.*?>\s+/tmp/',    # echo to /tmp
        r'printf\s+.*?>\s+/tmp/',  # printf to /tmp
        r'tee\s+/tmp/',            # tee to /tmp
        r'touch\s+/tmp/',          # touch in /tmp
        r'mkdir\s+(-p\s+)?/tmp/',  # mkdir in /tmp
    ]
    
    @classmethod
    def is_safe_command(cls, command: str) -> Tuple[bool, str]:
        """Check if command is safe to execute."""
        if not command or not command.strip():
            return False, "Empty command"
        
        # Check if it's a safe write operation to /tmp
        import re
        for pattern in cls.SAFE_WRITE_PATTERNS:
            if re.search(pattern, command):
                # It's a safe write to /tmp, allow it
                return True, "OK"
        
        # Check for dangerous commands
        cmd_lower = command.lower()
        for dangerous in cls.DANGEROUS_COMMANDS:
            if dangerous in cmd_lower:
                return False, f"Dangerous command detected: {dangerous}"
        
        # Block write operations outside /tmp
        if '>' in command and '/tmp/' not in command:
            return False, "File write operations only allowed in /tmp directory"
        
        return True, "OK"
    
    @classmethod
    def execute(cls, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Execute shell command safely.
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        is_safe, reason = cls.is_safe_command(command)
        if not is_safe:
            return False, "", f"Command rejected: {reason}"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
    
    @classmethod
    def display_result(cls, success: bool, stdout: str, stderr: str) -> None:
        """Display command execution result with rich formatting."""
        if success:
            console.print("\n[bold green]✓ Command executed successfully[/bold green]\n")
            if stdout:
                console.print("[bold cyan]Output:[/bold cyan]")
                syntax = Syntax(stdout, "bash", theme="monokai", line_numbers=False)
                console.print(syntax)
        else:
            console.print("\n[bold red]✗ Command failed[/bold red]\n")
            if stderr:
                console.print("[bold red]Error:[/bold red]")
                console.print(f"[red]{stderr}[/red]")
