# Single-File AI Agent (Sandboxed Workspace) Tutorial

A fully working AI agent in a **single Python file** — no frameworks, no complexity.

This agent can read, write, edit, copy, move, and delete files **inside a protected workspace folder only**, enforced by a sandbox system. It interacts naturally through a conversational interface powered by **OpenRouter-compatible LLMs**.

Everything runs with inline dependencies using `uv`, so you don’t need `pip install`, virtual environments, or separate setup.

You will learn how AI agents:

- parse model responses  
- call tools automatically  
- execute file operations  
- maintain conversation state  
- operate safely inside a restricted folder  

A full real-world agent implementation with the mechanics exposed — no abstractions hiding the logic.

## Credits

This repository is inspired by Francis Beeson's implementation:  
**Single-File AI Agent Tutorial**  
<https://github.com/leobeeson/single-file-ai-agent-tutorial>

Core architecture follows Thorsten Ball’s guide:  
**“How to Build an Agent”** — ampcode.com  

Huge credit to both authors.

## Features

### 🎯 Core Agent Features
- Pure single-file implementation  
- No virtual environments  
- No manual dependencies (handled automatically by `uv`)  
- Sandboxed workspace folder:  
  - Agent cannot escape outside this directory  
  - All file paths are validated with secure resolution  

### 🛠️ Supported Tools
The AI agent can:

- Read files  
- List directories  
- Edit or create files  
- Delete files and directories  
- Create directories  
- Copy files  
- Move files  

All operations are restricted to the workspace.

### 💬 Interaction
- Fully interactive chat interface  
- Natural language file manipulation  
- Automatic tool invocation  
- Persistent conversation context  
- Logging of tool calls to `agent.log`  

### 🔐 Safety
- Attempts to use `../` or absolute paths outside the workspace **are blocked**  
- All paths go through a secure resolver  

## Requirements

- `uv` package manager  
- Python 3.12+ (automatically handled by `uv`)  
- **OpenRouter API key**  
  (Get from: https://openrouter.ai/settings/keys)

## Installing uv

`uv` is a fast Python package manager that supports inline script dependencies and isolated execution environments.

### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
```

## Running the Agent

1. Export your OpenRouter API key:

### Linux/macOS
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### Windows (PowerShell)
```powershell
setx OPENROUTER_API_KEY "your-key-here"
```

2. Run the agent:

```bash
uv run main.py
```

`uv` automatically installs all dependencies defined in the script header.

## How the Sandbox Works

The script enforces a single fixed workspace directory:

```python
PROJECT_ROOT = "/home/yourname/agent_workspace"
os.makedirs(PROJECT_ROOT, exist_ok=True)
os.chdir(PROJECT_ROOT)
```

Path resolution uses:

- absolute normalization  
- prefix validation  
- restriction to `PROJECT_ROOT`  

Any path escaping the workspace raises:

```
Access denied outside workspace
```

This protects your system while allowing powerful file manipulation inside the designated folder.

## License

This project is licensed under the MIT License — see the **LICENSE** file for details.
