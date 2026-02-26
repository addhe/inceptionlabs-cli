import os
import click
import requests
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def get_api_key():
    """Helper to get API key and show error if missing."""
    api_key = os.environ.get("INCEPTION_API_KEY")
    if not api_key:
        click.secho("Error: INCEPTION_API_KEY environment variable is not set.", fg="red", err=True)
        click.secho("Please set it or create a .env file with INCEPTION_API_KEY=your_key", fg="yellow", err=True)
    return api_key

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

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--model', default='mercury-2', help='Model to use for interactive chat (default: mercury-2)')
@click.option('--max-tokens', default=8192, help='Maximum number of tokens to generate (default: 8192)')
def cli(ctx, model, max_tokens):
    """InceptionLabs CLI tool. Run without arguments to enter interactive chat mode."""
    if ctx.invoked_subcommand is None:
        interactive_chat(model, max_tokens)

def interactive_chat(model, max_tokens):
    """Interactive chat mode similar to Claude CLI."""
    api_key = get_api_key()
    if not api_key:
        return

    click.secho(f"Welcome to InceptionLabs CLI!", fg="cyan", bold=True)
    click.secho(f"Using model: {model}", fg="cyan")
    click.secho("Type '/exit' or '/bye' to quit.\n", fg="yellow")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.inceptionlabs.ai/v1"
    )

    history = [{"role": "system", "content": "You are a helpful AI assistant."}]

    try:
        while True:
            try:
                # Prompt user
                user_input = click.prompt(click.style("You", fg="green", bold=True))
                
                # Check for exit commands
                if user_input.strip().lower() in ['/exit', '/bye']:
                    break
                
                if not user_input.strip():
                    continue

                # Add user message to history
                history.append({"role": "user", "content": user_input})
                
                # Call API
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=history,
                        max_tokens=max_tokens
                    )
                    
                    assistant_msg = response.choices[0].message.content
                    
                    # Print response
                    click.secho("\nAssistant:", fg="blue", bold=True)
                    click.echo(assistant_msg)
                    click.echo() # Empty line for spacing
                    
                    # Add assistant message to history
                    history.append({"role": "assistant", "content": assistant_msg})
                    
                except Exception as e:
                    error_msg = str(e)
                    click.secho(f"API Error: {error_msg}", fg="red", err=True)
                    if "early_access_required" in error_msg:
                        click.secho("Note: This model currently requires early access.", fg="yellow", err=True)
                        click.secho("You can sign up here: https://www.inceptionlabs.ai/early-access", fg="yellow", err=True)
                    
                    # Remove the user message that caused the error so they can try again
                    history.pop()

            except (KeyboardInterrupt, EOFError):
                # Handle Ctrl+C or Ctrl+D
                break
                
    finally:
        # Save history when exiting
        save_chat_history(history, model)
        click.secho("\nGoodbye! Session history saved.", fg="cyan")

@cli.command()
@click.argument('prompt', type=str)
@click.option('--model', default='mercury-2', help='Model to use for completion (default: mercury-2)')
@click.option('--max-tokens', default=8192, help='Maximum number of tokens to generate (default: 8192)')
def ask(prompt, model, max_tokens):
    """Ask a question or send a prompt to InceptionLabs AI."""
    api_key = get_api_key()
    if not api_key:
        return

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.inceptionlabs.ai/v1"
        )
        
        click.secho(f"Sending prompt to {model}...", fg="cyan")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        click.secho("\nResponse:", fg="green", bold=True)
        click.echo(response.choices[0].message.content)
        
    except Exception as e:
        error_msg = str(e)
        click.secho(f"Error: {error_msg}", fg="red", err=True)
        if "early_access_required" in error_msg:
            click.secho("\nNote: Mercury-2 currently requires early access.", fg="yellow", err=True)
            click.secho("You can sign up here: https://www.inceptionlabs.ai/early-access", fg="yellow", err=True)

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
        click.secho(f"Requesting FIM completion from {model}...", fg="cyan")
        
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
        
        click.secho("\nCompletion:", fg="green", bold=True)
        click.echo(response.json()['choices'][0]['text'])
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.secho(f"Response: {e.response.text}", fg="red", err=True)

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
        click.secho(f"Applying changes using {model}...", fg="cyan")
        
        content = f"<|original_code|>\n{original_code}\n<|/original_code|>\n\n<|update_snippet|>\n{update_snippet}\n<|/update_snippet|>"
        
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
        
        click.secho("\nResult:", fg="green", bold=True)
        click.echo(response.json()['choices'][0]['message']['content'])
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.secho(f"Response: {e.response.text}", fg="red", err=True)

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
        click.secho(f"Requesting edit completion from {model}...", fg="cyan")
        
        content = f"<|recently_viewed_code_snippets|>\n{recently_viewed}\n<|/recently_viewed_code_snippets|>\n\n"
        content += f"<|current_file_content|>\ncurrent_file_path: {file_path}\n{file_content}\n<|code_to_edit|>\n{code_to_edit}\n<|/code_to_edit|>\n<|/current_file_content|>\n\n"
        content += f"<|edit_diff_history|>\n{edit_diff_history}\n<|/edit_diff_history|>"
        
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
        
        click.secho("\nCompletion:", fg="green", bold=True)
        click.echo(response.json()['choices'][0]['message']['content'])
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        if hasattr(e, 'response') and e.response is not None:
            click.secho(f"Response: {e.response.text}", fg="red", err=True)

if __name__ == '__main__':
    cli()
