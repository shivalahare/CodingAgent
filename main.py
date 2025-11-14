# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai",
#     "pydantic",
#     "python-dotenv",
# ]
# ///

import os
import sys
import argparse
import logging
import json
import importlib.util
from typing import List, Dict, Any, Callable
from openai import OpenAI  # type: ignore
from pydantic import BaseModel  # type: ignore
from dotenv import load_dotenv

# -------------------- Environment Setup --------------------
load_dotenv()

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent.log"), logging.StreamHandler(sys.stdout)],
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


# -------------------- Tool Definition (schemas only) --------------------
class Tool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


# -------------------- AI Agent --------------------
class AIAgent:
    def __init__(self, api_key: str, tools_dir: str = "tools"):
        self.client = OpenAI(api_key=api_key, base_url="https://router.huggingface.co/v1")
        self.messages: List[Dict[str, Any]] = []
        self.tools_dir = tools_dir

        # tool_name -> loaded python function
        self.dynamic_tool_functions: Dict[str, Callable[..., str]] = {}

        self._setup_tool_schemas()
        self._load_dynamic_tools()

    # ----------- Tool Schemas (for LLM visibility only) ------------
    def _setup_tool_schemas(self):
        self.tools = [
            Tool(
                name="read_file",
                description="Read a file from disk",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            Tool(
                name="list_files",
                description="List files in a directory",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": [],
                },
            ),
            Tool(
                name="edit_file",
                description="Edit a file, replacing old_text with new_text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "old_text": {"type": "string"},
                        "new_text": {"type": "string"},
                    },
                    "required": ["path", "new_text"],
                },
            ),
            Tool(
                name="delete_file",
                description="Delete a file or directory",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            Tool(
                name="create_directory",
                description="Create a directory",
                input_schema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            Tool(
                name="copy_file",
                description="Copy file from source to destination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "destination_path": {"type": "string"},
                    },
                    "required": ["source_path", "destination_path"],
                },
            ),
            Tool(
                name="move_file",
                description="Move or rename a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "destination_path": {"type": "string"},
                    },
                    "required": ["source_path", "destination_path"],
                },
            ),
            Tool(
                name="search_file",
                description="Search files for matching text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string"},
                        "search_text": {"type": "string"},
                        "file_extension": {"type": "string"},
                    },
                    "required": ["directory", "search_text"],
                },
            ),
        ]

    # ----------- Load tool implementations from /tools/*.py --------
    def _load_dynamic_tools(self):
        if not os.path.isdir(self.tools_dir):
            logging.warning("Tools directory '%s' does not exist.", self.tools_dir)
            return

        for file in sorted(os.listdir(self.tools_dir)):
            if not file.endswith(".py"):
                continue

            module_name = file[:-3]
            file_path = os.path.join(self.tools_dir, file)

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                logging.error("Failed to load %s: %s", file, str(e))
                continue

            if hasattr(module, module_name):
                func = getattr(module, module_name)
                if callable(func):
                    self.dynamic_tool_functions[module_name] = func
                    logging.info("Loaded tool: %s", module_name)
                else:
                    logging.warning("Function %s in %s is not callable", module_name, file)
            else:
                logging.warning("File %s has no function '%s'", file, module_name)

    # ----------- Execute tool by name -----------
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        if tool_name not in self.dynamic_tool_functions:
            return f"Error: Tool '{tool_name}' is not implemented."

        fn = self.dynamic_tool_functions[tool_name]
        try:
            return fn(**tool_input)  # your tools return strings
        except Exception as e:
            logging.exception("Tool error")
            return f"Tool '{tool_name}' failed: {str(e)}"

    # ----------- Chat Loop with tool calling ----------
    def chat(self, user_input: str, model: str = "deepseek-ai/DeepSeek-V3.2-Exp:novita") -> str:
        self.messages.append({"role": "user", "content": user_input})

        tools_payload = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                },
            }
            for t in self.tools
        ]

        while True:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.messages,
                tools=tools_payload,
                tool_choice="auto",
            )

            msg = response.choices[0].message
            self.messages.append(msg)

            # Tool-call?
            if msg.tool_calls:
                results = []
                for call in msg.tool_calls:
                    tool_name = call.function.name
                    args = json.loads(call.function.arguments or "{}")
                    output = self._execute_tool(tool_name, args)
                    results.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": output,
                    })
                self.messages.extend(results)
                continue

            # Final answer
            return msg.content or ""


# -------------------- CLI --------------------
def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant (HF Router, Dynamic Tools Only)")
    parser.add_argument("--api-key", help="HF_TOKEN or environment variable")
    parser.add_argument("--tools-dir", default="tools", help="Tools folder (default: tools/)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("HF_TOKEN")
    if not api_key:
        print("Missing API key. Set HF_TOKEN or pass --api-key")
        sys.exit(1)

    agent = AIAgent(api_key=api_key, tools_dir=args.tools_dir)

    print("AI Code Assistant — HuggingFace Router")
    print("Dynamic Tool Loader (no built-in tools)")
    print("----------------------------------------")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        response = agent.chat(user_input)
        print("Assistant:", response)


if __name__ == "__main__":
    main()
