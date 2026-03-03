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
🖥️ **Shell Command Execution** - Execute terminal commands safely from within the CLI
🤖 **AI-Powered Command Detection** - AI automatically detects and executes shell commands from natural language
🏗️ **Clean Code Architecture** - Modular design with separation of concerns

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
- **`/shell <command>`** - Execute shell command (e.g., `/shell ls -la /tmp`)
- **`/exit`** or **`/bye`** - Exit the CLI

**Shell Command Examples:**

*Manual execution with /shell:*
```bash
# Check files in /tmp directory
You > /shell ls -la /tmp

# Count files
You > /shell ls /tmp | wc -l

# Check disk usage
You > /shell df -h

# View current directory
You > /shell pwd
```

*AI-powered natural language (automatic detection & execution):*
```bash
# AI detects the need and executes automatically
You > ada berapa file di /tmp ?
Assistant: I'll check the number of files in /tmp directory.
{"cmd":["bash","-lc","find /tmp -maxdepth 1 -type f | wc -l"]}
🔧 Detected command: find /tmp -maxdepth 1 -type f | wc -l
✓ Command executed successfully
Output: 42

# Another example
You > ada berapa folder dan files di directory ini ?
Assistant: Let me count the folders and files in the current directory.
{"cmd":["bash","-lc","echo 'Folders:' && find . -maxdepth 1 -type d | wc -l && echo 'Files:' && find . -maxdepth 1 -type f | wc -l"]}
🔧 Detected command: echo 'Folders:' && find . -maxdepth 1 -type d | wc -l...
✓ Command executed successfully
Output:
Folders: 5
Files: 8
```

**Safety Features:**
- ⚠️ Dangerous commands are blocked (rm, sudo, format, etc.)
- ⏱️ Commands timeout after 30 seconds
- 🔒 Safe execution with proper error handling

The CLI features:
- 🎨 Rich terminal UI with colored output
- ⚡ Real-time streaming responses
- 💾 Auto-save sessions after each exchange
- 📝 Command history with auto-suggest (use ↑/↓ arrows)
- 🔄 Automatic session persistence
- 🖥️ Safe shell command execution

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

## Architecture

The CLI follows clean code principles with a modular architecture:

```
cli-inceptionlabs/
├── cli.py                    # Main CLI entry point
├── core/                     # Core modules
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── session.py           # Session and history management
│   ├── api_client.py        # InceptionLabs API client
│   ├── ui.py                # User interface utilities
│   ├── commands.py          # Command handler
│   ├── shell_executor.py    # Safe shell command execution
│   └── ai_shell_detector.py # AI-powered command detection
├── memory/                  # Chat history storage
└── requirements.txt
```

**Design Principles:**
- 🎯 **Single Responsibility** - Each module has one clear purpose
- 🔌 **Dependency Injection** - Easy to test and extend
- 🛡️ **Type Hints** - Better code clarity and IDE support
- 🧪 **Testable** - Modular design enables unit testing
- 📦 **Reusable** - Core modules can be imported elsewhere

## What's New

**v2.2 - AI-Powered Shell Detection:**
- 🤖 AI automatically detects when to execute shell commands
- 💬 Natural language queries trigger automatic command execution
- 🎯 Smart command extraction from AI responses
- 📝 Seamless integration with chat flow
- ✨ No need to manually use /shell for common queries

**v2.1 - Clean Code & Shell Execution:**
- 🏗️ Complete refactor with clean code architecture
- 🖥️ Shell command execution with safety checks
- 🔒 Dangerous command blocking
- 📁 Modular core package structure
- 🎯 Type hints throughout codebase

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
