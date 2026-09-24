from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage

def filter_tool_messages(messages: list[AnyMessage]) -> list[HumanMessage | AIMessage]:
    """
    Filters out messages that are tool messages.

    Args:
        messages (list): List of message dictionaries.

    Returns:
        list: Filtered list of message dictionaries.
    """
    return [msg for msg in messages[:-4] if not isinstance(msg, ToolMessage)] + messages[-4:]