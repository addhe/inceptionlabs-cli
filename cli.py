import os
import sys
import json
import click
import requests
import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize Rich console
console = Console()

def get_api_key():
    """Helper to get API key and show error if missing."""
    api_key = os.environ.get("INCEPTION_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] INCEPTION_API_KEY environment variable is not set.")
        console.print("[yellow]Please set it or create a .env file with INCEPTION_API_KEY=your_key[/yellow]")
    return api_key

def get_session_file():
    """Get the session history file path."""
    session_dir = Path.home() / ".inception" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / "last_session.json"

def save_session(history, model):
    """Save current session for resume."""
    session_file = get_session_file()
    session_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "model": model,
        "history": history
    }
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

def load_session():
    """Load last session if exists."""
    session_file = get_session_file()
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_chat_history(history, model):
    """Save chat history to memory/{date}.md"""
    if not history or len(history) <= 1:  # Only system prompt
        return
        
    os.makedirs("memory", exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    file_path = f"memory/{date_str}.md"
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## Session: {time_str} (Model: {model})\n\n")
        for msg in history:
            if msg["role"] == "system":
                continue
            role = "User" if msg["role"] == "user" else "Assistant"
            f.write(f"**{role}:**\n{msg['content']}\n\n")

def print_welcome(model):
    """Print welcome message."""
    console.print(Panel.fit(
        "[bold cyan]Welcome to InceptionLabs CLI![/bold cyan]\n"
        f"Using model: [yellow]{model}[/yellow]\n\n"
        "[dim]Commands:[/dim]\n"
        "  [green]/help[/green]    - Show available commands\n"
        "  [green]/clear[/green]   - Clear conversation history\n"
        "  [green]/resume[/green]  - Resume last session\n"
        "  [green]/exit[/green]    - Exit the CLI\n"
        "  [green]/bye[/green]     - Exit the CLI",
        title="🚀 InceptionLabs",
        border_style="cyan"
    ))

def handle_command(cmd, history, model):
    """Handle special commands."""
    cmd = cmd.strip().lower()
    
    if cmd == "/help":
        console.print("\n[bold cyan]Available Commands:[/bold cyan]")
        console.print("  [green]/help[/green]    - Show this help message")
        console.print("  [green]/clear[/green]   - Clear conversation history")
        console.print("  [green]/resume[/green]  - Resume last session")
        console.print("  [green]/exit[/green]    - Exit the CLI")
        console.print("  [green]/bye[/green]     - Exit the CLI\n")
        return "continue", history
    
    elif cmd == "/clear":
        console.print("[yellow]Conversation history cleared.[/yellow]\n")
        return "clear", [{"role": "system", "content": "You are a helpful AI assistant."}]
    
    elif cmd == "/resume":
        session = load_session()
        if session and session.get("history"):
            console.print(f"[green]Resumed session from {session['timestamp']}[/green]\n")
            return "continue", session["history"]
        else:
            console.print("[yellow]No previous session found.[/yellow]\n")
            return "continue", history
    
    elif cmd in ["/exit", "/bye"]:
        return "exit", history
    
    return None, history

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--model', default='mercury-2', help='Model to use for interactive chat (default: mercury-2)')
@click.option('--max-tokens', default=8192, help='Maximum number of tokens to generate (default: 8192)')
@click.option('-r', '--resume', is_flag=True, help='Resume last session')
@click.option('-p', '--prompt', type=str, help='One-shot prompt without entering interactive mode')
def cli(ctx, model, max_tokens, resume, prompt):
    """InceptionLabs CLI tool. Run without arguments to enter interactive chat mode."""
    if ctx.invoked_subcommand is None:
        if prompt:
            # One-shot mode
            one_shot_prompt(prompt, model, max_tokens)
        else:
            # Interactive mode
            interactive_chat(model, max_tokens, resume)

def one_shot_prompt(prompt, model, max_tokens):
    """Execute a single prompt and exit."""
    api_key = get_api_key()
    if not api_key:
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.inceptionlabs.ai/v1"
    )

    try:
        with console.status(f"[cyan]Asking {model}...", spinner="dots"):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True
            )
        
        console.print()
        for chunk in response:
            if chunk.choices[0].delta.content:
                console.print(chunk.choices[0].delta.content, end="")
        console.print("\n")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def interactive_chat(model, max_tokens, resume=False):
    """Interactive chat mode with rich terminal UI."""
    api_key = get_api_key()
    if not api_key:
        return

    print_welcome(model)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.inceptionlabs.ai/v1"
    )

    # Initialize or resume history
    if resume:
        session = load_session()
        if session and session.get("history"):
            history = session["history"]
            console.print(f"[green]✓ Resumed session from {session['timestamp']}[/green]\n")
        else:
            history = [{"role": "system", "content": "You are a helpful AI assistant."}]
            console.print("[yellow]No previous session found. Starting fresh.[/yellow]\n")
    else:
        history = [{"role": "system", "content": "You are a helpful AI assistant."}]

    # Setup prompt with history
    history_file = Path.home() / ".inception" / "history.txt"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    session = PromptSession(history=FileHistory(str(history_file)))

    try:
        while True:
            try:
                # Get user input with auto-suggest
                user_input = session.prompt(
                    "You > ",
                    auto_suggest=AutoSuggestFromHistory()
                )
                
                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.strip().startswith("/"):
                    action, history = handle_command(user_input, history, model)
                    if action == "exit":
                        break
                    elif action in ["continue", "clear"]:
                        continue

                # Add user message to history
                history.append({"role": "user", "content": user_input})
                
                # Call API with streaming
                try:
                    console.print()
                    with console.status("[cyan]Thinking...", spinner="dots"):
                        response = client.chat.completions.create(
                            model=model,
                            messages=history,
                            max_tokens=max_tokens,
                            stream=True
                        )
                    
                    # Stream response
                    console.print("[bold blue]Assistant:[/bold blue]")
                    assistant_msg = ""
                    
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            assistant_msg += content
                            console.print(content, end="")
                    
                    console.print("\n")
                    
                    # Add assistant message to history
                    history.append({"role": "assistant", "content": assistant_msg})
                    
                    # Save session after each exchange
                    save_session(history, model)
                    
                except Exception as e:
                    error_msg = str(e)
                    console.print(f"[bold red]API Error:[/bold red] {error_msg}")
                    if "early_access_required" in error_msg:
                        console.print("[yellow]Note: This model currently requires early access.[/yellow]")
                        console.print("[yellow]Sign up: https://www.inceptionlabs.ai/early-access[/yellow]")
                    
                    # Remove the user message that caused the error
                    history.pop()

            except (KeyboardInterrupt, EOFError):
                console.print("\n")
                break
                
    finally:
        # Save history when exiting
        save_chat_history(history, model)
        save_session(history, model)
        console.print("[cyan]👋 Goodbye! Session saved.[/cyan]")

@cli.command()
@click.argument('prompt', type=str)
@click.option('--model', default='mercury-2', help='Model to use for completion (default: mercury-2)')
@click.option('--max-tokens', default=8192, help='Maximum number of tokens to generate (default: 8192)')
@click.option('--stream/--no-stream', default=True, help='Stream the response (default: True)')
def ask(prompt, model, max_tokens, stream):
    """Ask a question or send a prompt to InceptionLabs AI."""
    api_key = get_api_key()
    if not api_key:
        return

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.inceptionlabs.ai/v1"
        )
        
        with console.status(f"[cyan]Asking {model}...", spinner="dots"):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=stream
            )
        
        console.print("\n[bold green]Response:[/bold green]")
        
        if stream:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    console.print(chunk.choices[0].delta.content, end="")
            console.print("\n")
        else:
            md = Markdown(response.choices[0].message.content)
            console.print(md)
        
    except Exception as e:
        error_msg = str(e)
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        if "early_access_required" in error_msg:
            console.print("[yellow]Note: Mercury-2 currently requires early access.[/yellow]")
            console.print("[yellow]Sign up: https://www.inceptionlabs.ai/early-access[/yellow]")

@cli.command()
@click.argument('prompt', type=str)
@click.argument('suffix', type=str)
@click.option('--model', default='mercury-edit', help='Model to use (default: mercury-edit)')
@click.option('--max-tokens', default=512, help='Maximum tokens to generate (default: 512)')
def fim(prompt, suffix, model, max_tokens):
    """Fill-in-the-middle completion."""
    api_key = get_api_key()
    if not api_key:
        return

    try:
        with console.status(f"[cyan]Requesting FIM from {model}...", spinner="dots"):
            response = requests.post(
                'https://api.inceptionlabs.ai/v1/fim/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                json={
                    "model": model,
                    "prompt": prompt,
                    "suffix": suffix,
                    "max_tokens": max_tokens
                }
            )
        response.raise_for_status()
        
        completion = response.json()['choices'][0]['text']
        console.print("\n[bold green]Completion:[/bold green]")
        syntax = Syntax(completion, "python", theme="monokai", line_numbers=False)
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            console.print(f"[red]Response: {e.response.text}[/red]")

@cli.command()
@click.argument('original_code', type=str)
@click.argument('update_snippet', type=str)
@click.option('--model', default='mercury-edit', help='Model to use (default: mercury-edit)')
@click.option('--max-tokens', default=8192, help='Maximum tokens to generate (default: 8192)')
def apply(original_code, update_snippet, model, max_tokens):
    """Apply an update snippet to original code."""
    api_key = get_api_key()
    if not api_key:
        return

    try:
        content = f"<|original_code|>\n{original_code}\n<|/original_code|>\n\n<|update_snippet|>\n{update_snippet}\n<|/update_snippet|>"
        
        with console.status(f"[cyan]Applying changes with {model}...", spinner="dots"):
            response = requests.post(
                'https://api.inceptionlabs.ai/v1/apply/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": content}
                    ],
                    "max_tokens": max_tokens
                }
            )
        response.raise_for_status()
        
        result = response.json()['choices'][0]['message']['content']
        console.print("\n[bold green]Result:[/bold green]")
        syntax = Syntax(result, "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            console.print(f"[red]Response: {e.response.text}[/red]")

@cli.command()
@click.argument('file_path', type=str)
@click.argument('file_content', type=str)
@click.argument('code_to_edit', type=str)
@click.argument('edit_diff_history', type=str, default="")
@click.argument('recently_viewed', type=str, default="")
@click.option('--model', default='mercury-edit', help='Model to use (default: mercury-edit)')
@click.option('--max-tokens', default=8192, help='Maximum tokens to generate (default: 8192)')
def edit(file_path, file_content, code_to_edit, edit_diff_history, recently_viewed, model, max_tokens):
    """Edit code with cursor context and history."""
    api_key = get_api_key()
    if not api_key:
        return

    try:
        content = f"<|recently_viewed_code_snippets|>\n{recently_viewed}\n<|/recently_viewed_code_snippets|>\n\n"
        content += f"<|current_file_content|>\ncurrent_file_path: {file_path}\n{file_content}\n<|code_to_edit|>\n{code_to_edit}\n<|/code_to_edit|>\n<|/current_file_content|>\n\n"
        content += f"<|edit_diff_history|>\n{edit_diff_history}\n<|/edit_diff_history|>"
        
        with console.status(f"[cyan]Requesting edit from {model}...", spinner="dots"):
            response = requests.post(
                'https://api.inceptionlabs.ai/v1/edit/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": content}
                    ],
                    "max_tokens": max_tokens
                }
            )
        response.raise_for_status()
        
        completion = response.json()['choices'][0]['message']['content']
        console.print("\n[bold green]Completion:[/bold green]")
        syntax = Syntax(completion, "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            console.print(f"[red]Response: {e.response.text}[/red]")

if __name__ == '__main__':
    cli()
