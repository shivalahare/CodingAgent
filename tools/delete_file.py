import os
import shutil


def delete_file(path: str) -> str:
    """
    Delete a file or directory at the specified path.
    
    Args:
        path (str): The path to the file or directory to delete
        
    Returns:
        str: Success or error message
    """
    try:
        if not os.path.exists(path):
            return f"Path not found: {path}"
        
        if os.path.isfile(path):
            os.remove(path)
            return f"Successfully deleted file: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Successfully deleted directory: {path}"
        else:
            return f"Unknown file type: {path}"
            
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error deleting {path}: {str(e)}"


if __name__ == "__main__":
    # Test the function
    result = delete_file("test_delete.txt")
    print(result)