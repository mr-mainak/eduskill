import base64

# Load and encode image
def encode_image_base64(image_path: str) -> str:
    """
    Function to encode image to base64 from path.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")