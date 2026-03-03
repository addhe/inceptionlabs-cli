from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()

class UI:
    """User interface utilities."""
    
    @staticmethod
    def print_welcome(model: str) -> None:
        """Print welcome message."""
        console.print(Panel.fit(
            "[bold cyan]Welcome to InceptionLabs CLI![/bold cyan]\n"
            f"Using model: [yellow]{model}[/yellow]\n\n"
            "[dim]Commands:[/dim]\n"
            "  [green]/help[/green]    - Show available commands\n"
            "  [green]/clear[/green]   - Clear conversation history\n"
            "  [green]/resume[/green]  - Resume last session\n"
            "  [green]/shell[/green]   - Execute shell command\n"
            "  [green]/exit[/green]    - Exit the CLI\n"
            "  [green]/bye[/green]     - Exit the CLI",
            title="🚀 InceptionLabs",
            border_style="cyan"
        ))
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print error message."""
        console.print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print success message."""
        console.print(f"[green]{message}[/green]")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message."""
        console.print(f"[yellow]{message}[/yellow]")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print info message."""
        console.print(f"[cyan]{message}[/cyan]")
    
    @staticmethod
    def print_code(code: str, language: str = "python", line_numbers: bool = True) -> None:
        """Print syntax-highlighted code."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=line_numbers)
        console.print(syntax)
    
    @staticmethod
    def print_markdown(content: str) -> None:
        """Print markdown content."""
        md = Markdown(content)
        console.print(md)
    
    @staticmethod
    def print_help() -> None:
        """Print help message."""
        console.print("\n[bold cyan]Available Commands:[/bold cyan]")
        console.print("  [green]/help[/green]    - Show this help message")
        console.print("  [green]/clear[/green]   - Clear conversation history")
        console.print("  [green]/resume[/green]  - Resume last session")
        console.print("  [green]/shell <cmd>[/green] - Execute shell command (e.g., /shell ls -la)")
        console.print("  [green]/exit[/green]    - Exit the CLI")
        console.print("  [green]/bye[/green]     - Exit the CLI\n")
