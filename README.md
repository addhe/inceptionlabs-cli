# InceptionLabs CLI

A powerful command-line interface for interacting with the InceptionLabs API, inspired by Claude Code. Features include interactive chat with streaming responses, rich terminal UI, session management, and specialized code editing capabilities.

## Features

✨ **Interactive Chat Mode** - Conversational AI with context awareness
🎨 **Rich Terminal UI** - Beautiful output with syntax highlighting and markdown rendering
⚡ **Streaming Responses** - Real-time response streaming for better UX
💾 **Session Management** - Resume previous conversations seamlessly
🔧 **Code Editing Tools** - FIM, Apply, and Edit commands for code manipulation
📝 **Command History** - Auto-suggest from previous commands
🎯 **One-Shot Mode** - Quick queries without entering interactive mode

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

### Interactive Chat Mode

The main way to use the CLI is through interactive chat mode with streaming responses and rich formatting.

**Start a new session:**
```bash
python cli.py
```

**Resume your last session:**
```bash
python cli.py --resume
# or
python cli.py -r
```

**Use a specific model:**
```bash
python cli.py --model mercury-2
```

#### Available Commands in Interactive Mode

Once in interactive mode, you can use these commands:

- **`/help`** - Show available commands
- **`/clear`** - Clear conversation history
- **`/resume`** - Resume last session
- **`/exit`** or **`/bye`** - Exit the CLI

The CLI features:
- 🎨 Rich terminal UI with colored output
- ⚡ Real-time streaming responses
- 💾 Auto-save sessions after each exchange
- 📝 Command history with auto-suggest (use ↑/↓ arrows)
- 🔄 Automatic session persistence

### One-Shot Mode

Execute a single prompt without entering interactive mode:

```bash
python cli.py -p "Explain quantum computing in simple terms"
# or
python cli.py --prompt "What is a diffusion model?"
```

### Command-Line Tools

#### 1. Ask (Single Query)

Ask a question with streaming response:

```bash
python cli.py ask "What is a diffusion model?"
```

Options:
- `--model` - Specify model (default: mercury-2)
- `--max-tokens` - Maximum tokens to generate (default: 8192)
- `--stream/--no-stream` - Enable/disable streaming (default: enabled)

Example:
```bash
python cli.py ask "Explain async/await in Python" --model mercury-2 --max-tokens 500
```

#### 2. FIM (Fill-in-the-Middle)

Complete code between a prefix and suffix with syntax highlighting:

```bash
python cli.py fim "def fibonacci(" "return a + b"
```

Features:
- Syntax-highlighted output
- Optimized for code completion
- Default max_tokens: 512

#### 3. Apply (Code Update)

Apply changes to existing code using an update snippet:

```bash
python cli.py apply "<original_code_here>" "<update_snippet_here>"
```

Example:
```bash
python cli.py apply "class Calculator:\n    def add(self, a, b):\n        return a + b" "def multiply(self, a, b):\n    return a * b"
```

#### 4. Edit (Context-Aware Edit)

Edit code with full context including file content, diff history, and recently viewed files:

```bash
python cli.py edit "solver.py" "<file_content>" "<code_to_edit>" "<diff_history>" "<recently_viewed>"
```

All code editing commands feature:
- 🎨 Syntax highlighting with line numbers
- 🔍 Context-aware suggestions
- ⚡ Fast processing with mercury-edit model

## Session Management

Sessions are automatically saved to `~/.inception/sessions/last_session.json` and can be resumed at any time.

**Chat history** is also saved to `memory/YYYY-MM-DD.md` for long-term reference.

**Command history** is stored in `~/.inception/history.txt` and provides auto-suggestions.

## Advanced Usage

### Piping and Scripting

Use one-shot mode for scripting:

```bash
# Quick query
python cli.py -p "summarize this error" < error.log

# Chain commands
echo "What is Docker?" | python cli.py -p "$(cat -)"
```

### Model Selection

Available models:
- **mercury-2** - Most powerful chat model (default for chat/ask)
- **mercury-edit** - Specialized for code editing (default for fim/apply/edit)

```bash
# Use specific model
python cli.py --model mercury-2
python cli.py ask "question" --model mercury-2
```

## Global Options

Most commands support these options:
- `--model` - Specify the model to use (defaults vary by command). For `ask`, the default is `mercury-2`.
- `--max-tokens` - Set the maximum number of tokens to generate (default: `8192` for most, `512` for `fim`).

Example with options:
```bash
python cli.py ask "Explain quantum computing in simple terms" --model mercury-2 --max-tokens 500
```

## Keyboard Shortcuts

In interactive mode:
- **↑/↓** - Navigate command history
- **Tab** - Auto-complete (when available)
- **Ctrl+C** or **Ctrl+D** - Exit gracefully

## Tips & Best Practices

1. **Use `/resume`** to continue where you left off
2. **Be specific** with your prompts for better results
3. **Use streaming** for real-time feedback on long responses
4. **Leverage command history** with arrow keys for repeated tasks
5. **Check `memory/` folder** for historical conversations

## Troubleshooting

**API Key Issues:**
```bash
# Check if API key is set
echo $INCEPTION_API_KEY

# Set it temporarily
export INCEPTION_API_KEY=your_key_here
```

**Model Access Errors:**
- Mercury-2 may require early access approval
- Sign up at: https://www.inceptionlabs.ai/early-access

**Session Issues:**
```bash
# Clear session cache
rm -rf ~/.inception/sessions/

# Clear command history
rm ~/.inception/history.txt
```

## What's New

**v2.0 - Claude Code Inspired Update:**
- ✨ Streaming responses for real-time feedback
- 🎨 Rich terminal UI with syntax highlighting
- 💾 Session management with resume capability
- 📝 Command history with auto-suggest
- 🎯 One-shot mode for quick queries
- 🔧 Improved error handling and user experience

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.
