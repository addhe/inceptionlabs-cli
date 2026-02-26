# InceptionLabs CLI

A command-line interface for interacting with the InceptionLabs API using the OpenAI Python client.

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd cli-inceptionlabs
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
Create a `.env` file in the root directory and add your InceptionLabs API key:
```env
INCEPTION_API_KEY=your_actual_api_key_here
```
Alternatively, set the environment variable directly:
```bash
export INCEPTION_API_KEY=your_actual_api_key_here
```

## Usage

The main entry point is `cli.py`. The CLI supports several commands for different types of AI interactions:

### 1. Ask (Chat Completion)
Ask questions directly from the command line:
```bash
python cli.py ask "What is a diffusion model?"
```

### 2. FIM (Fill-in-the-Middle)
Complete code between a prefix and suffix:
```bash
python cli.py fim "def fibonacci(" "return a + b" --model mercury-edit
```

### 3. Apply (Code Update)
Apply changes to existing code using an update snippet:
```bash
python cli.py apply "<original_code_here>" "<update_snippet_here>" --model mercury-edit
```

### 4. Edit (Context-Aware Edit)
Edit code with full context including file content, diff history, and recently viewed files:
```bash
python cli.py edit "solver.py" "<file_content>" "<code_to_edit>" "<diff_history>" "<recently_viewed>" --model mercury-edit
```

### Global Options

Most commands support these options:
* `--model`: Specify the model to use (defaults vary by command).
* `--max-tokens`: Set the maximum number of tokens to generate (default: `1000`).

Example with options:
```bash
python cli.py ask "Explain quantum computing in simple terms" --model mercury-2 --max-tokens 500
```
