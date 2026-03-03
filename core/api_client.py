import requests
from typing import Dict, Any, Iterator
from openai import OpenAI
from .config import Config

class InceptionLabsClient:
    """Client for InceptionLabs API interactions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.config = Config()
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.config.API_BASE_URL
        )
    
    def chat_completion(
        self,
        messages: list,
        model: str,
        max_tokens: int,
        stream: bool = False
    ) -> Any:
        """Create chat completion."""
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=stream
        )
    
    def fim_completion(
        self,
        prompt: str,
        suffix: str,
        model: str,
        max_tokens: int
    ) -> Dict:
        """Fill-in-the-middle completion."""
        response = requests.post(
            f'{self.config.API_BASE_URL}/fim/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
            },
            json={
                "model": model,
                "prompt": prompt,
                "suffix": suffix,
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        return response.json()
    
    def apply_completion(
        self,
        original_code: str,
        update_snippet: str,
        model: str,
        max_tokens: int
    ) -> Dict:
        """Apply code update."""
        content = f"<|original_code|>\n{original_code}\n<|/original_code|>\n\n<|update_snippet|>\n{update_snippet}\n<|/update_snippet|>"
        
        response = requests.post(
            f'{self.config.API_BASE_URL}/apply/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        return response.json()
    
    def edit_completion(
        self,
        file_path: str,
        file_content: str,
        code_to_edit: str,
        edit_diff_history: str,
        recently_viewed: str,
        model: str,
        max_tokens: int
    ) -> Dict:
        """Edit code with context."""
        content = f"<|recently_viewed_code_snippets|>\n{recently_viewed}\n<|/recently_viewed_code_snippets|>\n\n"
        content += f"<|current_file_content|>\ncurrent_file_path: {file_path}\n{file_content}\n<|code_to_edit|>\n{code_to_edit}\n<|/code_to_edit|>\n<|/current_file_content|>\n\n"
        content += f"<|edit_diff_history|>\n{edit_diff_history}\n<|/edit_diff_history|>"
        
        response = requests.post(
            f'{self.config.API_BASE_URL}/edit/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        return response.json()
