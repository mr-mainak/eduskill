from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time_and_date() -> str:
    """
    Returns the current system date and time as a formatted string.
    Example format: 'Thursday, 12 June 2025 - 14:45:30'
    
    Returns:
        str: Formatted current date and time.
    """
    now = datetime.now()
    return now.strftime("%A, %d %B %Y - %H:%M:%S")