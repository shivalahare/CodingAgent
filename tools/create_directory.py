import os


def create_directory(path: str) -> str:
    """
    Create a directory at the specified path.
    
    Args:
        path (str): The path to the directory to create
        
    Returns:
        str: Success or error message
    """
    try:
        if os.path.exists(path):
            if os.path.isdir(path):
                return f"Directory already exists: {path}"
            else:
                return f"Path exists but is not a directory: {path}"
        
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory: {path}"
        
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error creating directory {path}: {str(e)}"


if __name__ == "__main__":
    # Test the function
    result = create_directory("test_directory")
    print(result)