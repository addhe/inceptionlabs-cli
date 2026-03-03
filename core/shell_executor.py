import subprocess
import shlex
from typing import Tuple
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class ShellExecutor:
    """Execute shell commands safely."""
    
    DANGEROUS_COMMANDS = [
        'rm', 'rmdir', 'del', 'format', 'mkfs',
        'dd', 'shutdown', 'reboot', 'halt',
        '>', '>>', 'sudo', 'su'
    ]
    
    @classmethod
    def is_safe_command(cls, command: str) -> Tuple[bool, str]:
        """Check if command is safe to execute."""
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return False, "Empty command"
        
        base_cmd = cmd_parts[0].lower()
        
        for dangerous in cls.DANGEROUS_COMMANDS:
            if dangerous in command.lower():
                return False, f"Dangerous command detected: {dangerous}"
        
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
