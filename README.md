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

The main entry point is `cli.py`. You can ask questions directly from the command line:

```bash
python cli.py ask "What is a diffusion model?"
```

### Options

* `--model`: Specify the model to use (default: `mercury-2`).
* `--max-tokens`: Set the maximum number of tokens to generate (default: `1000`).

Example with options:
```bash
python cli.py ask "Explain quantum computing in simple terms" --model mercury-2 --max-tokens 500
```
