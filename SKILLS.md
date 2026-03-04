# Skills System

InceptionLabs CLI includes a powerful skills system that extends the AI's capabilities with specialized tools and integrations, similar to Claude Code, Gemini Skills, and OpenClaw.

## Overview

Skills are Python plugins that provide specific functionality to the AI assistant. The AI can automatically detect when to use a skill based on user queries, or you can invoke skills directly.

## Built-in Skills

### 1. File Analyzer (`file_analyzer`)

Analyze code files and directories to get insights about code structure, line counts, and language distribution.

**Parameters:**
- `path` (string, required): Path to file or directory to analyze
- `recursive` (boolean, optional): Recursively analyze directories (default: false)

**Examples:**
```
You > analyze the cli.py file
You > analyze the core directory recursively
```

**JSON format:**
```json
{"skill": "file_analyzer", "params": {"path": "cli.py"}}
{"skill": "file_analyzer", "params": {"path": "core", "recursive": true}}
```

**Output:**
- Language detection
- Total lines, code lines, comment lines, blank lines
- File size
- Directory summary with language breakdown

### 2. Web Search (`web_search`)

Search the web using DuckDuckGo Instant Answer API to get information and related topics.

**Parameters:**
- `query` (string, required): Search query

**Examples:**
```
You > search the web for Python best practices
You > what is clean code architecture
```

**JSON format:**
```json
{"skill": "web_search", "params": {"query": "Python programming"}}
```

**Output:**
- Abstract/summary of the topic
- Source URL
- Related topics with links

### 3. Git Helper (`git_helper`)

Perform common git operations like checking status, viewing logs, and listing branches.

**Parameters:**
- `operation` (string, required): Git operation - `status`, `log`, `diff`, `branches`, `current_branch`
- `path` (string, optional): Repository path (default: current directory)
- `limit` (integer, optional): Limit number of results for log operation (default: 10)

**Examples:**
```
You > show me the git status
You > what are the recent commits
You > list all git branches
```

**JSON format:**
```json
{"skill": "git_helper", "params": {"operation": "status"}}
{"skill": "git_helper", "params": {"operation": "log", "limit": 5}}
{"skill": "git_helper", "params": {"operation": "branches"}}
```

**Output:**
- Formatted git information
- Commit history with hash, author, date, message
- Branch lists
- Status information

## Using Skills

### Natural Language (Recommended)

Simply ask the AI naturally, and it will detect when to use a skill:

```bash
You > analyze the cli.py file and tell me how many lines it has
You > search for information about clean code principles
You > show me the last 5 git commits
```

### Direct JSON Invocation

You can also invoke skills directly using JSON format:

```bash
You > {"skill": "file_analyzer", "params": {"path": "cli.py"}}
```

### List Available Skills

Use the `/skills` command to see all available skills:

```bash
You > /skills
```

## Creating Custom Skills

You can create your own skills by adding Python files to the `skills/` directory.

### Skill Template

```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.skill_base import Skill, SkillMetadata, SkillParameter
from typing import Dict, Any

class MyCustomSkill(Skill):
    """Description of your skill."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            description="What your skill does",
            version="1.0.0",
            author="Your Name",
            parameters=[
                SkillParameter(
                    name="param1",
                    type="str",
                    description="Description of parameter",
                    required=True
                ),
                SkillParameter(
                    name="param2",
                    type="int",
                    description="Optional parameter",
                    required=False,
                    default=10
                )
            ],
            examples=[
                '{"skill": "my_skill", "params": {"param1": "value"}}',
            ]
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill logic."""
        param1 = kwargs.get("param1")
        param2 = kwargs.get("param2", 10)
        
        try:
            # Your skill logic here
            result = {"data": "your result"}
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### Skill Development Guidelines

1. **Inherit from `Skill` base class**
2. **Implement `get_metadata()`** - Define skill name, description, parameters
3. **Implement `execute()`** - Main skill logic
4. **Return proper format** - Always return dict with `success` and `result`/`error`
5. **Handle errors gracefully** - Catch exceptions and return error messages
6. **Use type hints** - For better code clarity
7. **Add examples** - Help users understand how to use your skill

### Parameter Types

Supported parameter types:
- `str` - String values
- `int` - Integer values
- `bool` - Boolean values
- `list` - List/array values

### Skill Loading

Skills are automatically loaded from the `skills/` directory when the CLI starts. The SkillManager will:
1. Scan the `skills/` directory for `.py` files
2. Import each file and look for `Skill` subclasses
3. Instantiate and register each skill
4. Make skills available to the AI system prompt

## Architecture

```
cli-inceptionlabs/
├── core/
│   ├── skill_base.py       # Base Skill class and metadata
│   ├── skill_manager.py    # Load and manage skills
│   └── skill_detector.py   # Detect and execute skills from AI
├── skills/
│   ├── __init__.py
│   ├── file_analyzer.py    # Built-in file analysis skill
│   ├── web_search.py       # Built-in web search skill
│   ├── git_helper.py       # Built-in git operations skill
│   └── your_skill.py       # Your custom skills
```

## Advanced Features

### Skill Chaining

Skills can be chained together by the AI:

```
You > analyze all Python files in the core directory and then search for best practices for the most common issues
```

The AI will:
1. Use `file_analyzer` to analyze Python files
2. Use `web_search` to find best practices based on findings

### Conditional Execution

The AI can decide when to use skills based on context:

```
You > if there are more than 100 lines in cli.py, search for refactoring techniques
```

### Error Handling

Skills have built-in error handling:
- Parameter validation
- Type checking
- Execution error catching
- User-friendly error messages

## Best Practices

1. **Keep skills focused** - One skill, one responsibility
2. **Validate inputs** - Use parameter validation
3. **Provide clear examples** - Help users understand usage
4. **Handle errors gracefully** - Return meaningful error messages
5. **Use rich output** - Format results nicely for terminal display
6. **Document thoroughly** - Clear descriptions and parameter docs
7. **Test your skills** - Ensure they work in various scenarios

## Troubleshooting

### Skill not loading

- Check that your skill file is in the `skills/` directory
- Ensure your class inherits from `Skill`
- Verify there are no syntax errors
- Check the CLI startup messages for loading errors

### Skill not executing

- Verify parameter names match metadata
- Check parameter types are correct
- Look for error messages in the output
- Use `/skills` to confirm skill is loaded

### AI not using skill

- Make your query more specific
- Try using the JSON format directly
- Check that the skill description matches your use case
- Ensure the skill is loaded (use `/skills`)

## Examples

### Example 1: Code Analysis Workflow

```bash
You > analyze the entire codebase recursively and tell me which languages are used

AI will use: file_analyzer with recursive=true
Output: Summary of all files, languages, and line counts
```

### Example 2: Research and Development

```bash
You > search for modern Python async patterns and then check if we're using them in our code

AI will:
1. Use web_search to find async patterns
2. Use file_analyzer to check code
3. Provide recommendations
```

### Example 3: Git Workflow

```bash
You > show me the git status and recent commits

AI will use: git_helper for both status and log operations
```

## Future Skills Ideas

- **Database Query** - Execute safe database queries
- **API Tester** - Test REST APIs
- **Code Formatter** - Format code using black, prettier, etc.
- **Documentation Generator** - Generate docs from code
- **Test Runner** - Run unit tests and show results
- **Package Manager** - Install/update dependencies
- **Linter** - Run linting tools
- **Security Checker** - Scan for security issues

## Contributing Skills

To contribute a new skill:

1. Create your skill in `skills/your_skill.py`
2. Follow the skill template and guidelines
3. Test thoroughly
4. Document with clear examples
5. Submit a pull request

---

**Note:** Skills run with the same permissions as the CLI, so be careful with skills that modify files or execute system commands. Always validate inputs and handle errors properly.
