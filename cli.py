import os
import click
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

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
    api_key = os.environ.get("INCEPTION_API_KEY")
    if not api_key:
        click.secho("Error: INCEPTION_API_KEY environment variable is not set.", fg="red", err=True)
        click.secho("Please set it or create a .env file with INCEPTION_API_KEY=your_key", fg="yellow", err=True)
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

if __name__ == '__main__':
    cli()
