import json


def load_config(config_path: str) -> dict:
    """
    Loads a JSON configuration file and returns its contents as a dictionary.

    Args:
        config_path (str): The file path to the JSON configuration file.

    Returns:
        dict: The parsed contents of the configuration file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    return config