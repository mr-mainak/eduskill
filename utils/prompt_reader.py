def load_prompt(filepath: str) -> str:
    """
    Reads the contents of a text file and returns it as a string.

    Args:
        filepath (str): The path to the text file containing the prompt.

    Returns:
        str: The full text content of the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If an error occurs during file reading.
    """
    with open(filepath, 'r') as prompt_file:
        return prompt_file.read()