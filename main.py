# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "openai",
#     "pydantic",
# ]
# ///

import os
import sys
import argparse
import logging
import json
import shutil
from typing import List, Dict, Any
from openai import OpenAI  # type: ignore
from pydantic import BaseModel  # type: ignore
from dotenv import load_dotenv

# -------------------- Environment Setup --------------------
load_dotenv()


# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("agent.log")],
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


# -------------------- Tool Definition --------------------
class Tool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


# -------------------- AI Agent --------------------
class AIAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        self.messages: List[Dict[str, Any]] = []
        self.tools: List[Tool] = []
        self._setup_tools()

    def _setup_tools(self):
        self.tools = [
            Tool(
                name="read_file",
                description="Read the contents of a file at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="list_files",
                description="List all files and directories in the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list (defaults to current directory)",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="edit_file",
                description="Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.",
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
                description="Delete a file or directory at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file or directory to delete",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="create_directory",
                description="Create a directory at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the directory to create",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="copy_file",
                description="Copy a file from source to destination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "The path to the source file",
                        },
                        "destination_path": {
                            "type": "string",
                            "description": "The path to the destination file",
                        }
                    },
                    "required": ["source_path", "destination_path"],
                },
            ),
            Tool(
                name="move_file",
                description="Move or rename a file from source to destination",
                input_schema={
                    "type": "object",
                    "properties": {
                        "source_path": {
                            "type": "string",
                            "description": "The path to the source file",
                        },
                        "destination_path": {
                            "type": "string",
                            "description": "The path to the destination file",
                        }
                    },
                    "required": ["source_path", "destination_path"],
                },
            ),
            Tool(
                name="search_file",
                description="Search for files containing specific text",
                input_schema={
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to search in",
                        },
                        "search_text": {
                            "type": "string",
                            "description": "The text to search for",
                        },
                        "file_extension": {
                            "type": "string",
                            "description": "Filter by file extension (e.g., '.txt', '.py')",
                        }
                    },
                    "required": ["directory", "search_text"],
                },
            ),
        ]

    # -------------------- Tool Implementations --------------------
    def _read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return f"File contents of {path}:\n{content}"
        except FileNotFoundError:
            return f"File not found: {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _list_files(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                return f"Path not found: {path}"

            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                prefix = "[DIR]" if os.path.isdir(item_path) else "[FILE]"
                items.append(f"{prefix} {item}")

            return f"Contents of {path}:\n" + "\n".join(items) if items else f"Empty directory: {path}"
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _edit_file(self, path: str, old_text: str, new_text: str) -> str:
        try:
            if os.path.exists(path) and old_text:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                if old_text not in content:
                    return f"Text not found in file: {old_text}"

                content = content.replace(old_text, new_text)
            else:
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                content = new_text

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"Successfully written to {path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        logging.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            if tool_name == "read_file":
                return self._read_file(tool_input["path"])
            elif tool_name == "list_files":
                return self._list_files(tool_input.get("path", "."))
            elif tool_name == "edit_file":
                return self._edit_file(
                    tool_input["path"], tool_input.get("old_text", ""), tool_input["new_text"]
                )
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            logging.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    # -------------------- Chat Loop --------------------
    def chat(self, user_input: str) -> str:
        logging.info(f"User input: {user_input}")
        self.messages.append({"role": "user", "content": user_input})

        tools = [
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
            try:
                response = self.client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3.1:free",
                    messages=self.messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7,
                )

                message = response.choices[0].message
                self.messages.append(message)

                # Handle tool calls if any
                if message.tool_calls:
                    tool_results = []
                    for call in message.tool_calls:
                        name = call.function.name
                        args = json.loads(call.function.arguments)
                        result = self._execute_tool(name, args)
                        tool_results.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result,
                            }
                        )

                    # Feed tool results back to the model
                    self.messages.extend(tool_results)
                    continue  # continue the loop until no more tool calls
                else:
                    reply = message.content or ""
                    return reply
            except Exception as e:
                return f"Error: {str(e)}"


# -------------------- CLI --------------------
def main():
    parser = argparse.ArgumentParser(
        description="AI Code Assistant (OpenRouter) - Conversational agent with file tools"
    )
    parser.add_argument(
        "--api-key", help="OpenRouter API key (or set OPENROUTER_API_KEY environment variable)"
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: Please provide an API key via --api-key or OPENROUTER_API_KEY environment variable")
        sys.exit(1)

    agent = AIAgent(api_key)

    print("AI Code Assistant (OpenRouter)")
    print("==============================")
    print("A conversational AI agent that can read, list, and edit files.")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            if not user_input:
                continue
            print("\nAssistant: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()
