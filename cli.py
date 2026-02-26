import os
import click
import requests
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

@click.group()
def cli():
    """InceptionLabs CLI tool"""
    pass

@cli.command()
@click.argument('prompt', type=str)
@click.option('--model', default='mercury-2', help='Model to use for completion (default: mercury-2)')
@click.option('--max-tokens', default=1000, help='Maximum number of tokens to generate (default: 1000)')
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
        click.secho(f"Error: {str(e)}", fg="red", err=True)

@cli.command()
@click.argument('prompt', type=str)
@click.argument('suffix', type=str)
@click.option('--model', default='mercury-edit', help='Model to use (default: mercury-edit)')
@click.option('--max-tokens', default=1000, help='Maximum tokens to generate (default: 1000)')
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
@click.option('--max-tokens', default=1000, help='Maximum tokens to generate (default: 1000)')
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
@click.option('--max-tokens', default=1000, help='Maximum tokens to generate (default: 1000)')
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
