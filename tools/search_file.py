import os


def search_file(directory: str, search_text: str, file_extension: str = None) -> str:
    """
    Search for files containing specific text.
    
    Args:
        directory (str): The directory to search in
        search_text (str): The text to search for
        file_extension (str, optional): Filter by file extension (e.g., '.txt', '.py')
        
    Returns:
        str: List of files containing the search text
    """
    try:
        if not os.path.exists(directory):
            return f"Directory not found: {directory}"
        
        if not os.path.isdir(directory):
            return f"Path is not a directory: {directory}"
        
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file_extension and not file.endswith(file_extension):
                    continue
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_text.lower() in content.lower():
                            results.append(file_path)
                except:
                    # Skip files that can't be read (binary files, etc.)
                    continue
        
        if not results:
            return f"No files found containing '{search_text}' in {directory}"
        
        return f"Files containing '{search_text}':\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error searching in {directory}: {str(e)}"


if __name__ == "__main__":
    # Test the function
    result = search_file("..", "def", ".py")
    print(result)