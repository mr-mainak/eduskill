def extract_text_from_message(message) -> str:
    '''
    Extract text like System, AI, Human messages from the state of the graph.
    As image is encoded to base64 and put inside the state, When passing to the LLM, context increases.
    Imlemented only for the sementic search node
    '''

    content = message.content

    if isinstance(content, str):
        text = content

    elif isinstance(content, list):

        text_parts = []

        for item in content:

            if not isinstance(item, dict):
                continue

            if item.get("type") == "text":
                text_parts.append(
                    item.get("text", "")
                )

        text = "\n".join(text_parts)

    else:
        text = str(content)

    if not text:
        return ""

    if message.type == "human":
        role = "User"

    elif message.type == "ai":
        role = "Assistant"

    else:
        role = message.type.capitalize()

    return f"{role}: {text}"