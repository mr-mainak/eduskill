from src.general_purpose.graph import create_general_purpose_graph
from api.dtos.general_purpose_assistant import GeneralPurposeAssistantInputModel
from langchain_core.messages import HumanMessage, SystemMessage
from typing import AsyncGenerator, Optional, Annotated
# from src.services.langfuse_service import langfuse_handler
# from phoenix.otel import register
import os
from fastapi import Request, UploadFile, File, Form


# os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://192.168.1.31:6006"

# # configure the Phoenix tracer
# tracer_provider = register(
#   project_name="yellow-panda2", # Default is 'default'
#   endpoint="http://192.168.1.31:6006/v1/traces",
#   auto_instrument=True # Auto-instrument your app based on installed OI dependencies
# )

general_purpose_assistant_graph = create_general_purpose_graph()


import base64

from langchain_core.messages import HumanMessage, SystemMessage


async def stream_general_purpose_assistant(
    request: Request,
    data: GeneralPurposeAssistantInputModel,
    image: Optional[UploadFile] = File(None),
) -> AsyncGenerator:
    """
    Stream general-purpose assistant responses.

    The image is optional. If provided, it is included in the
    HumanMessage so that it becomes part of the conversation history.
    """

    states = []
    isbr = False

    # -----------------------------------------
    # Create user message
    # -----------------------------------------

    if image is not None:

        image_bytes = await image.read()

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        human_message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": data.query,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:{image.content_type};"
                            f"base64,{image_base64}"
                        )
                    },
                },
            ]
        )

        image_data = {
            "content_type": image.content_type,
            "filename": image.filename,
        }

    else:

        human_message = HumanMessage(
            content=data.query
        )

        image_data = None

    # -----------------------------------------
    # Run graph
    # -----------------------------------------

    for stream_mode, chunk in general_purpose_assistant_graph.stream(
        {
            "messages": [human_message],
            "project_id": data.project_id,
            "image": image_data,
        },
        config={
            "recursion_limit": 25,
            "run_name": "general purpose assistant",
            "tags": ["study"],
            "configurable": {
                "thread_id": "1"
            },
        },
        stream_mode=["messages", "values"]
    ):

        # -----------------------------------------
        # Client disconnected
        # -----------------------------------------

        if await request.is_disconnected():

            general_purpose_assistant_graph.update_state(
                config={
                    "configurable": {
                        "thread_id": "1"
                    }
                },
                values={
                    "messages": [
                        SystemMessage(
                            content=(
                                "Do not answer the previous question. "
                                "It was stopped by the user."
                            ),
                            metadata={
                                "status": "interrupted"
                            },
                        )
                    ],
                },
            )

            print(
                "Client disconnected. Stopping the stream."
            )
            break

        # -----------------------------------------
        # Store graph states
        # -----------------------------------------

        if stream_mode == "values":
            states.append(chunk)

        # -----------------------------------------
        # Stream messages
        # -----------------------------------------

        if stream_mode == "messages":

            message, metadata = chunk

            if metadata["langgraph_node"] in [
                "semantic_search_agent",
                "normal_llm_agent",
            ]:

                print(message.content, end="")

                if message.content in ["<br", "<br>"]:
                    isbr = True
                    continue

                elif isbr and message.content == ">":
                    isbr = False
                    continue

                else:
                    isbr = False
                    yield message.content

    print("Teaching assistant finished streaming.")