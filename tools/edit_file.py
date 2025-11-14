import os

def edit_file(path: str, new_text: str, old_text: str = "") -> str:
    """
    Edit a file by replacing old_text with new_text.
    If old_text is empty, overwrite the file entirely.
    Creates the file and directories if they don't exist.
    """
    # Ensure parent folder exists
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    # If file exists and old_text was provided, perform replace
    if os.path.exists(path) and old_text:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if old_text not in content:
            return f"Text not found in {path}: {old_text}"

        content = content.replace(old_text, new_text)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully edited {path}"

    # Otherwise overwrite or create file
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)

    return f"Successfully wrote {path}"



if __name__ == "__main__":
    edit_file(
        path="test.txt",
        old_text="Hello world!",
        new_text="Hello world! How are you?",
    )
