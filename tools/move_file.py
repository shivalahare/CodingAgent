import os
import shutil


def move_file(source_path: str, destination_path: str) -> str:
    """
    Move or rename a file from source to destination.
    
    Args:
        source_path (str): The path to the source file
        destination_path (str): The path to the destination file
        
    Returns:
        str: Success or error message
    """
    try:
        if not os.path.exists(source_path):
            return f"Source file not found: {source_path}"
        
        if os.path.isdir(source_path):
            return f"Source is a directory, not a file: {source_path}"
        
        # Create parent directories if they don't exist
        dest_dir = os.path.dirname(destination_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        
        shutil.move(source_path, destination_path)
        return f"Successfully moved {source_path} to {destination_path}"
        
    except PermissionError:
        return f"Permission denied: {source_path} -> {destination_path}"
    except Exception as e:
        return f"Error moving {source_path} to {destination_path}: {str(e)}"


if __name__ == "__main__":
    # Test the function
    result = move_file("test_file.txt", "renamed_test_file.txt")
    print(result)