import subprocess
import shlex
from typing import Tuple
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class ShellExecutor:
    """Execute shell commands safely."""

    # Commands that are actually dangerous when executed
    DANGEROUS_COMMANDS = [
        r'\brm\s+-rf\b',      # rm -rf (always dangerous)
        r'\brm\s+.*\s+-rf\b', # rm with -rf anywhere
        r'\brmdir\b',         # rmdir
        r'\bmkfs\b',          # mkfs (format filesystem)
        r'\bdd\s+',           # dd command
        r'\bshutdown\b',      # shutdown
        r'\breboot\b',        # reboot
        r'\bhalt\b',          # halt
        r'\bsudo\b',          # sudo
        r'\bsu\b',            # su
        r'\bchmod\s+777\b',   # chmod 777
        r'\bchown\b',         # chown
    ]

    SAFE_WRITE_PATTERNS = [
        r'cat\s+<<.*?>\s+/tmp/',  # heredoc to /tmp
        r'cat\s+>\s+/tmp/',        # cat redirect to /tmp
        r'echo\s+.*?>\s+/tmp/',    # echo to /tmp
        r'printf\s+.*?>\s+/tmp/',  # printf to /tmp
        r'tee\s+/tmp/',            # tee to /tmp
        r'touch\s+/tmp/',          # touch in /tmp
        r'mkdir\s+(-p\s+)?/tmp/',  # mkdir in /tmp
    ]

    SAFE_CLEANUP_PATTERNS = [
        r'\brm\s+/tmp/tmpfile_\*',   # rm /tmp/tmpfile_*
        r'\brm\s+/tmp/test_\*',      # rm /tmp/test_*
        r'\brm\s+/tmp/temp_\*',      # rm /tmp/temp_*
        r'\brm\s+/tmp/.*\*',         # rm /tmp/pattern*
    ]

    @classmethod
    def is_safe_command(cls, command: str) -> Tuple[bool, str]:
        """Check if command is safe to execute."""
        if not command or not command.strip():
            return False, "Empty command"

        import re

        # Check if it's a safe write operation to /tmp
        for pattern in cls.SAFE_WRITE_PATTERNS:
            if re.search(pattern, command):
                return True, "OK"

        # Check if it's a safe cleanup pattern in /tmp
        for pattern in cls.SAFE_CLEANUP_PATTERNS:
            if re.search(pattern, command):
                # Still check for -rf flag
                if re.search(r'\brm\s+.*-rf', command):
                    return False, "rm -rf is not allowed"
                return True, "OK"

        # Check for dangerous commands using word boundaries
        for dangerous_pattern in cls.DANGEROUS_COMMANDS:
            if re.search(dangerous_pattern, command, re.IGNORECASE):
                return False, f"Dangerous command detected"

        # Block write operations outside /tmp (but allow in echo strings)
        # Only check for redirects that are actual commands, not in strings
        if re.search(r'(?<!["\'])>\s+(?!/tmp/)', command):
            # Check if it's not within quotes
            parts = command.split('>')
            if len(parts) > 1:
                # Check if the redirect target is not /tmp
                target = parts[1].strip().split()[0] if parts[1].strip() else ""
                if target and not target.startswith('/tmp/') and not target.startswith("'") and not target.startswith('"'):
                    return False, "File write operations only allowed in /tmp directory"

        return True, "OK"

    @classmethod
    def fix_macos_incompatible_commands(cls, command: str) -> str:
        """
        Auto-fix common Linux commands that don't work on macOS.

        Returns:
            Fixed command string
        """
        import re

        # Fix: date +%s%N (Linux) -> python3 timing (macOS compatible)
        # Replace date +%s%N with python3 millisecond timing
        if 'date +%s%N' in command:
            command = re.sub(
                r'\$\(date \+%s%N\)',
                "$(python3 -c 'import time; print(int(time.time()*1000000000))')",
                command
            )

        return command

    @classmethod
    def execute(cls, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """
        Execute shell command safely.

        Returns:
            Tuple of (success, stdout, stderr)
        """
        # Auto-fix macOS incompatible commands
        command = cls.fix_macos_incompatible_commands(command)

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
