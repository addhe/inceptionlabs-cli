import click
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.console import Console

from core.config import Config
from core.session import SessionManager
from core.api_client import InceptionLabsClient
from core.ui import UI
from core.commands import CommandHandler
from core.shell_executor import ShellExecutor

console = Console()
ui = UI()
config = Config()

def validate_api_key() -> str:
    """Validate and return API key."""
    api_key = config.get_api_key()
    if not api_key:
        ui.print_error("INCEPTION_API_KEY environment variable is not set.")
        ui.print_warning("Please set it or create a .env file with INCEPTION_API_KEY=your_key")
    return api_key

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--model', default=None, help='Model to use for interactive chat')
@click.option('--max-tokens', default=None, type=int, help='Maximum number of tokens to generate')
@click.option('-r', '--resume', is_flag=True, help='Resume last session')
@click.option('-p', '--prompt', type=str, help='One-shot prompt without entering interactive mode')
def cli(ctx, model, max_tokens, resume, prompt):
    """InceptionLabs CLI tool. Run without arguments to enter interactive chat mode."""
    model = model or config.DEFAULT_CHAT_MODEL
    max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
    
    if ctx.invoked_subcommand is None:
        if prompt:
            one_shot_prompt(prompt, model, max_tokens)
        else:
            interactive_chat(model, max_tokens, resume)

def one_shot_prompt(prompt: str, model: str, max_tokens: int) -> None:
    """Execute a single prompt and exit."""
    api_key = validate_api_key()
    if not api_key:
        return

    client = InceptionLabsClient(api_key)

    try:
        with console.status(f"[cyan]Asking {model}...", spinner="dots"):
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=max_tokens,
                stream=True
            )
        
        console.print()
        for chunk in response:
            if chunk.choices[0].delta.content:
                console.print(chunk.choices[0].delta.content, end="")
        console.print("\n")
        
    except Exception as e:
        ui.print_error(str(e))

def interactive_chat(model: str, max_tokens: int, resume: bool = False) -> None:
    """Interactive chat mode with rich terminal UI and shell execution."""
    api_key = validate_api_key()
    if not api_key:
        return

    ui.print_welcome(model)
    
    client = InceptionLabsClient(api_key)
    session_manager = SessionManager()
    command_handler = CommandHandler(session_manager)

    # Initialize or resume history
    if resume:
        session = session_manager.load_session()
        if session and session.get("history"):
            history = session["history"]
            ui.print_success(f"✓ Resumed session from {session['timestamp']}\n")
        else:
            history = [{"role": "system", "content": "You are a helpful AI assistant with shell command execution capabilities."}]
            ui.print_warning("No previous session found. Starting fresh.\n")
    else:
        history = [{"role": "system", "content": "You are a helpful AI assistant with shell command execution capabilities."}]

    # Setup prompt with history
    prompt_session = PromptSession(
        history=FileHistory(str(config.get_history_file()))
    )

    try:
        while True:
            try:
                user_input = prompt_session.prompt(
                    "You > ",
                    auto_suggest=AutoSuggestFromHistory()
                )
                
                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.strip().startswith("/"):
                    action, history = command_handler.handle(user_input, history, model)
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
                        response = client.chat_completion(
                            messages=history,
                            model=model,
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
                    session_manager.save_session(history, model)
                    
                except Exception as e:
                    error_msg = str(e)
                    ui.print_error(f"API Error: {error_msg}")
                    if "early_access_required" in error_msg:
                        ui.print_warning("Note: This model currently requires early access.")
                        ui.print_warning("Sign up: https://www.inceptionlabs.ai/early-access")
                    history.pop()

            except (KeyboardInterrupt, EOFError):
                console.print("\n")
                break
                
    finally:
        session_manager.save_chat_history(history, model)
        session_manager.save_session(history, model)
        ui.print_info("👋 Goodbye! Session saved.")

@cli.command()
@click.argument('prompt', type=str)
@click.option('--model', default=None, help='Model to use for completion')
@click.option('--max-tokens', default=None, type=int, help='Maximum number of tokens to generate')
@click.option('--stream/--no-stream', default=True, help='Stream the response (default: True)')
def ask(prompt, model, max_tokens, stream):
    """Ask a question or send a prompt to InceptionLabs AI."""
    api_key = validate_api_key()
    if not api_key:
        return
    
    model = model or config.DEFAULT_CHAT_MODEL
    max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
    client = InceptionLabsClient(api_key)

    try:
        with console.status(f"[cyan]Asking {model}...", spinner="dots"):
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=model,
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
            ui.print_markdown(response.choices[0].message.content)
        
    except Exception as e:
        error_msg = str(e)
        ui.print_error(error_msg)
        if "early_access_required" in error_msg:
            ui.print_warning("Note: Mercury-2 currently requires early access.")
            ui.print_warning("Sign up: https://www.inceptionlabs.ai/early-access")

@cli.command()
@click.argument('prompt', type=str)
@click.argument('suffix', type=str)
@click.option('--model', default=None, help='Model to use')
@click.option('--max-tokens', default=None, type=int, help='Maximum tokens to generate')
def fim(prompt, suffix, model, max_tokens):
    """Fill-in-the-middle completion."""
    api_key = validate_api_key()
    if not api_key:
        return
    
    model = model or config.DEFAULT_EDIT_MODEL
    max_tokens = max_tokens or config.DEFAULT_FIM_MAX_TOKENS
    client = InceptionLabsClient(api_key)

    try:
        with console.status(f"[cyan]Requesting FIM from {model}...", spinner="dots"):
            result = client.fim_completion(prompt, suffix, model, max_tokens)
        
        completion = result['choices'][0]['text']
        console.print("\n[bold green]Completion:[/bold green]")
        ui.print_code(completion, "python", line_numbers=False)
        
    except Exception as e:
        ui.print_error(str(e))
        if hasattr(e, 'response') and e.response is not None:
            ui.print_error(f"Response: {e.response.text}")

@cli.command()
@click.argument('original_code', type=str)
@click.argument('update_snippet', type=str)
@click.option('--model', default=None, help='Model to use')
@click.option('--max-tokens', default=None, type=int, help='Maximum tokens to generate')
def apply(original_code, update_snippet, model, max_tokens):
    """Apply an update snippet to original code."""
    api_key = validate_api_key()
    if not api_key:
        return
    
    model = model or config.DEFAULT_EDIT_MODEL
    max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
    client = InceptionLabsClient(api_key)

    try:
        with console.status(f"[cyan]Applying changes with {model}...", spinner="dots"):
            result = client.apply_completion(original_code, update_snippet, model, max_tokens)
        
        code_result = result['choices'][0]['message']['content']
        console.print("\n[bold green]Result:[/bold green]")
        ui.print_code(code_result, "python", line_numbers=True)
        
    except Exception as e:
        ui.print_error(str(e))
        if hasattr(e, 'response') and e.response is not None:
            ui.print_error(f"Response: {e.response.text}")

@cli.command()
@click.argument('file_path', type=str)
@click.argument('file_content', type=str)
@click.argument('code_to_edit', type=str)
@click.argument('edit_diff_history', type=str, default="")
@click.argument('recently_viewed', type=str, default="")
@click.option('--model', default=None, help='Model to use')
@click.option('--max-tokens', default=None, type=int, help='Maximum tokens to generate')
def edit(file_path, file_content, code_to_edit, edit_diff_history, recently_viewed, model, max_tokens):
    """Edit code with cursor context and history."""
    api_key = validate_api_key()
    if not api_key:
        return
    
    model = model or config.DEFAULT_EDIT_MODEL
    max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
    client = InceptionLabsClient(api_key)

    try:
        with console.status(f"[cyan]Requesting edit from {model}...", spinner="dots"):
            result = client.edit_completion(
                file_path, file_content, code_to_edit,
                edit_diff_history, recently_viewed, model, max_tokens
            )
        
        completion = result['choices'][0]['message']['content']
        console.print("\n[bold green]Completion:[/bold green]")
        ui.print_code(completion, "python", line_numbers=True)
        
    except Exception as e:
        ui.print_error(str(e))
        if hasattr(e, 'response') and e.response is not None:
            ui.print_error(f"Response: {e.response.text}")

if __name__ == '__main__':
    cli()
