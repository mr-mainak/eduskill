# Eduskill Multimodal Assistant

A multimodal educational assistant built with **FastAPI, LangGraph, LangChain, and Ollama**.

The assistant supports:

* Normal text-based questions
* Optional image uploads
* Multimodal conversations
* Image-aware follow-up questions
* LangGraph-based routing
* Semantic search for knowledge-based questions
* Tool calling
* Streaming LLM responses
* Conversation state using LangGraph checkpointing

---

## Architecture

The request flows through the system as follows:

```text
                         Client
                           │
                           │ multipart/form-data
                           ▼
                    ┌──────────────┐
                    │   FastAPI    │
                    │              │
                    │ query        │
                    │ project_id   │
                    │ image        │
                    └──────┬───────┘
                           │
                           ▼
              GeneralPurposeAssistantInputModel
                           │
                           ▼
                       Handler
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
              Text query        Image file
                                    │
                                    ▼
                              Base64 encoding
                                    │
                  └────────┬────────┘
                           ▼
                    HumanMessage
                           │
                           ▼
                       LangGraph
                           │
                           ▼
                     image_router
                      /          \
                     /            \
                 Image          No Image
                   │                │
                   ▼                ▼
             normal_llm_agent  query_type_decider
                                    │
                            ┌───────┴────────┐
                            ▼                ▼
                     semantic_search    normal_llm
                            │                │
                            └───────┬────────┘
                                    ▼
                               Tool Executor
                                    │
                                    ▼
                              Streaming Output
```

---

# 1. Project Overview

Eduskill is an AI-powered educational assistant designed to provide tutoring and learning assistance to students.

The system uses LangGraph to control the execution flow and supports both:

```text
Text-only conversations
```

and:

```text
Text + Image conversations
```

For example:

```text
User:
"What is this component?"

+ uploads:

[breadboard.jpg]
```

The image and question are converted into a multimodal `HumanMessage` and passed through the LangGraph workflow.

---

# 2. Technology Stack

* Python
* FastAPI
* Pydantic
* LangChain
* LangGraph
* Ollama
* Multimodal LLM
* Async Python
* HTTP multipart/form-data

---

# 3. API Endpoint

The main endpoint is:

```text
POST /general-purpose-assistant/
```

The endpoint accepts:

```text
multipart/form-data
```

### Parameters

| Parameter    | Type   | Required | Description        |
| ------------ | ------ | -------: | ------------------ |
| `query`      | string |      Yes | User's question    |
| `project_id` | string |      Yes | Project identifier |
| `image`      | file   |       No | Optional image     |

---

# 4. Example Request

## Text-only request

```bash
curl -X POST "http://localhost:8012/general-purpose-assistant/" \
  -F "query=what is a light sensor" \
  -F "project_id=6a43bdc0ac9539fbe50f3d82"
```

## Image request

```bash
curl -X POST "http://localhost:8012/general-purpose-assistant/" \
  -F "query=what is this component?" \
  -F "project_id=6a43bdc0ac9539fbe50f3d82" \
  -F "image=@/home/mainak/breadboard.jpg"
```

The `Content-Type` header does not need to be manually specified. `curl` automatically creates the correct `multipart/form-data` request.

---

# 5. Why Multipart Form Data?

A normal JSON request looks like:

```json
{
  "query": "What is a light sensor?",
  "project_id": "123"
}
```

This works well for text.

However, the request also needs to carry an image file.

Therefore the API uses:

```text
multipart/form-data
```

The request contains separate parts:

```text
query       → text
project_id  → text
image       → binary file
```

FastAPI handles these parts using:

```python
query: str = Form(...)
project_id: str = Form(...)
image: UploadFile | None = File(None)
```

---

# 6. API Route

The API route is responsible for parsing the HTTP request.

```python
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from api.dtos.general_purpose_assistant import (
    GeneralPurposeAssistantInputModel
)

from api.handlers.general_purpose_assistant import (
    stream_general_purpose_assistant
)


general_purpose_assistant_router = APIRouter(
    prefix="/general-purpose-assistant"
)


@general_purpose_assistant_router.post("/")
async def stream_output(
    request: Request,
    query: str = Form(...),
    project_id: str = Form(...),
    image: UploadFile | None = File(None),
):

    data = GeneralPurposeAssistantInputModel(
        query=query,
        project_id=project_id,
    )

    return StreamingResponse(
        content=stream_general_purpose_assistant(
            request,
            data,
            image,
        ),
    )
```

---

# 7. Why the DTO Is Created in the Route

The DTO is:

```python
from pydantic import BaseModel, Field


class GeneralPurposeAssistantInputModel(BaseModel):

    query: str = Field(
        ...,
        description="Question from the user"
    )

    project_id: str = Field(
        ...,
        description="Specified project id"
    )
```

The DTO represents application-level data:

```text
GeneralPurposeAssistantInputModel
│
├── query
└── project_id
```

The image is handled separately because it is a file upload.

The route therefore converts:

```text
multipart/form-data
```

into:

```text
GeneralPurposeAssistantInputModel
+
UploadFile
```

This keeps HTTP parsing separate from application logic.

---

# 8. Handler

The handler receives already-parsed application data:

```python
async def stream_general_purpose_assistant(
    request: Request,
    data: GeneralPurposeAssistantInputModel,
    image: Optional[UploadFile] = None,
) -> AsyncGenerator:
```

Notice that the handler does **not** use:

```python
Form()
```

or:

```python
File()
```

Those belong at the FastAPI route boundary.

The handler is responsible for:

1. Reading the uploaded image
2. Encoding the image
3. Creating the LangChain `HumanMessage`
4. Creating the LangGraph state
5. Running the graph
6. Streaming the response

---

# 9. Creating the Multimodal Message

When no image is provided:

```python
human_message = HumanMessage(
    content=data.query
)
```

The LLM receives a normal text message.

When an image is provided:

```python
image_bytes = await image.read()

image_base64 = base64.b64encode(
    image_bytes
).decode("utf-8")
```

The image is converted into Base64.

A multimodal message is then created:

```python
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
```

The resulting message conceptually looks like:

```text
HumanMessage
│
└── content
    │
    ├── text
    │     └── "What is this component?"
    │
    └── image
          └── base64 encoded image
```

This is the message that travels through LangGraph.

---

# 10. LangGraph State

The graph state contains:

```python
from typing import Annotated, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class GeneralPurposeState(TypedDict):

    messages: Annotated[list, add_messages]

    project_id: str

    caller: str

    image: Optional[dict]
```

The state has two different image-related concepts.

## `messages`

Contains the actual image:

```python
HumanMessage(
    content=[
        {
            "type": "text",
            "text": "What is this component?"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg;base64,..."
            }
        }
    ]
)
```

## `image`

Contains image metadata:

```python
{
    "content_type": "image/jpeg",
    "filename": "breadboard.jpg"
}
```

The metadata is used primarily for routing.

The actual image remains inside the `HumanMessage`.

---

# 11. Image Router

The graph starts with an image router.

```python
from typing import Literal
from langgraph.types import Command


def image_router(
    state: GeneralPurposeState
) -> Command[
    Literal[
        "query_type_decider",
        "normal_llm_agent"
    ]
]:

    if state.get("image") is not None:

        return Command(
            goto="normal_llm_agent"
        )

    return Command(
        goto="query_type_decider"
    )
```

The purpose of this node is to decide:

```text
Was an image uploaded?
```

If yes:

```text
normal_llm_agent
```

If no:

```text
query_type_decider
```

---

# 12. Graph Routing

The complete graph is conceptually:

```text
START
  │
  ▼
image_router
  │
  ├──────────── image ────────────► normal_llm_agent
  │
  │
  └────────── no image ───────────► query_type_decider
                                      │
                           ┌──────────┴──────────┐
                           ▼                     ▼
                  semantic_search_agent   normal_llm_agent
                           │                     │
                           └──────────┬──────────┘
                                      ▼
                         should_call_tool_executor
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                       tool_executor         END
                              │
                              ▼
                             END
```

---

# 13. Query Type Decider

For text-only questions, the `query_type_decider` determines whether the question requires semantic search or can be answered directly by the LLM.

Conceptually:

```text
User question
     │
     ▼
query_type_decider
     │
     ├── Knowledge/document question
     │          │
     │          ▼
     │    semantic_search_agent
     │
     └── General question
                │
                ▼
          normal_llm_agent
```

Images bypass this decision and are sent directly to the multimodal LLM agent.

---

# 14. Filtering Tool Messages

The application uses:

```python
def filter_tool_messages(messages):

    return [
        msg
        for msg in messages
        if not isinstance(msg, ToolMessage)
    ]
```

The important point is that this function removes `ToolMessage` objects.

It does **not** remove the image from a `HumanMessage`.

For example:

```text
HumanMessage
│
├── text
└── image
```

remains unchanged.

Therefore the image is still available to the multimodal LLM.

---

# 15. MessagesPlaceholder

The normal LLM node uses:

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
```

The prompt is constructed as:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(
        variable_name="messages"
    ),
])
```

The important distinction is:

```text
filter_tool_messages()
```

decides:

> Which messages should be passed?

While:

```text
MessagesPlaceholder()
```

decides:

> Where should those messages be inserted into the chat prompt?

Therefore the final LLM input can look like:

```text
SYSTEM
You are Eduskill...

HUMAN
What is this component?

IMAGE
[breadboard image]
```

---

# 16. Normal LLM Node

A simplified version:

```python
def normal_llm_search_node(
    state: GeneralPurposeState
) -> GeneralPurposeState:

    system_prompt = load_prompt(
        "./prompts/normal_llm_search_agent_prompt.txt"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(
            variable_name="messages"
        ),
    ])

    config = load_config(
        "./config/normal_llm_agent_config.json"
    )

    llm_model = ChatOllama(**config)

    llm = llm_model.bind_tools(
        [get_current_time_and_date]
    )

    chain = prompt | llm

    filtered_messages = filter_tool_messages(
        state["messages"]
    )

    response = chain.invoke({
        "messages": filtered_messages[-7:]
    })

    return {
        "messages": [response],
        "caller": "normal_llm_agent",
    }
```

---

# 17. Why `MessagesPlaceholder` Is Important

An older approach might put something like:

```text
Question: {question}
```

inside the system prompt.

That is less suitable for multimodal conversation because the actual conversation contains structured messages.

With:

```python
MessagesPlaceholder(
    variable_name="messages"
)
```

LangChain receives the original `HumanMessage` objects.

This preserves:

* Text
* Images
* Previous user messages
* Previous AI messages
* Conversation structure

---

# 18. Streaming

The graph is executed using:

```python
general_purpose_assistant_graph.stream(
    ...
    stream_mode=["messages", "values"]
)
```

Two types of information are received.

### `values`

Contains graph state updates.

### `messages`

Contains LLM message chunks.

The handler streams relevant LLM output back to the client:

```python
yield message.content
```

The client therefore receives the answer incrementally instead of waiting for the entire response.

---

# 19. Client Disconnect Handling

The handler checks:

```python
if await request.is_disconnected():
```

If the client disconnects, the graph state is updated with an interruption message:

```python
SystemMessage(
    content=(
        "Do not answer the previous question. "
        "It was stopped by the user."
    ),
    metadata={
        "status": "interrupted"
    },
)
```

This prevents unnecessary continued processing after the client has gone away.

---

# 20. Conversation Memory

The graph is compiled with a checkpointer:

```python
checkpointer = MemorySaver()

return graph_builder.compile(
    checkpointer=checkpointer
)
```

This allows LangGraph to maintain state across calls using a `thread_id`.

The current development configuration uses:

```python
"thread_id": "1"
```

### Important production consideration

Do not use a fixed thread ID in a multi-user production system.

Instead, use a unique conversation/thread identifier:

```text
user_id + conversation_id
```

or another unique identifier.

For example:

```python
"configurable": {
    "thread_id": conversation_id
}
```

Otherwise different users/conversations can share the same graph state.

---

# 21. Project Structure

A possible project structure is:

```text
eduskill/
│
├── main.py
│
├── api/
│   ├── dtos/
│   │   └── general_purpose_assistant.py
│   │
│   ├── handlers/
│   │   └── general_purpose_assistant.py
│   │
│   └── routes/
│       └── general_purpose_assistant.py
│
├── src/
│   └── general_purpose/
│       ├── graph.py
│       ├── nodes/
│       │   ├── image_router.py
│       │   ├── query_type_decider.py
│       │   ├── semantic_search.py
│       │   └── normal_llm_agent.py
│       │
│       ├── states/
│       │   └── agent_state.py
│       │
│       └── tools/
│
├── prompts/
│   └── normal_llm_search_agent_prompt.txt
│
├── config/
│   └── normal_llm_agent_config.json
│
├── utils/
│   ├── config_reader.py
│   ├── prompt_reader.py
│   ├── filter_message.py
│   └── logger.py
│
└── README.md
```

The exact structure can be adapted to the repository.

---

# 22. Installation

Create and activate a Python environment:

```bash
python3 -m venv eduskill_env
source eduskill_env/bin/activate
```

Install the required dependencies:

```bash
pip install fastapi uvicorn
pip install langchain
pip install langgraph
pip install langchain-ollama
python-multipart
```

The exact dependency versions should be pinned in a `requirements.txt` file for production deployments.

---

# 23. Running the Server

Start the application:

```bash
python3 main.py
```

Example:

```text
INFO: Uvicorn running on http://0.0.0.0:8012
```

The API is then available at:

```text
http://localhost:8012
```

---

# 24. API Documentation

FastAPI automatically provides interactive API documentation.

Open:

```text
http://localhost:8012/docs
```

OpenAPI specification:

```text
http://localhost:8012/openapi.json
```

The OpenAPI schema is particularly useful for verifying that the endpoint expects:

```text
multipart/form-data
```

with:

```text
query
project_id
image
```

---

# 25. Debugging the Multipart Request

If FastAPI returns:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "data"],
      "msg": "Field required"
    }
  ]
}
```

check the generated OpenAPI schema:

```bash
curl -s http://localhost:8012/openapi.json > /tmp/openapi.json
```

Then inspect the endpoint:

```bash
python3 - <<'PY'
import json

with open("/tmp/openapi.json") as f:
    data = json.load(f)

print(
    json.dumps(
        data["paths"]["/general-purpose-assistant/"]["post"],
        indent=2
    )
)
PY
```

The recommended route should expose individual multipart fields:

```text
query
project_id
image
```

rather than requiring a single multipart field named `data`.

---

# 26. Design Principles

The multimodal implementation follows a layered architecture.

### HTTP layer

Responsible for:

```text
Form()
File()
UploadFile
```

### Application layer

Responsible for:

```text
Pydantic DTO
```

### LLM preparation layer

Responsible for:

```text
HumanMessage
```

### Graph layer

Responsible for:

```text
Routing
State
Tools
Conversation flow
```

### Model layer

Responsible for:

```text
LLM inference
Multimodal understanding
Tool calling
```

This separation makes the system easier to debug and extend.

---

# 27. Important Concept

The image exists at two different levels:

```text
                    Uploaded Image
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       HumanMessage               State["image"]
              │                       │
              │                       │
       Actual image data          Metadata only
              │                       │
              ▼                       ▼
        Multimodal LLM             Routing
```

The actual image is stored inside the `HumanMessage`.

The `state["image"]` field is used as a routing signal and contains only metadata.

---

# 28. Future Improvements

Potential improvements for production:

* Replace the fixed `thread_id` with a unique conversation ID.
* Add authentication and authorization.
* Add image size/type validation.
* Add maximum upload size limits.
* Validate supported image MIME types.
* Add structured logging.
* Add request IDs for tracing.
* Add persistent LangGraph checkpoint storage.
* Add conversation expiration/cleanup.
* Add rate limiting.
* Add monitoring and metrics.
* Pin dependency versions.
* Add automated tests for text-only and multimodal requests.
* Add integration tests for image follow-up conversations.
* Add retry/error handling for LLM inference.
* Add GPU/model health checks.

---

# 29. Summary

The multimodal request follows this pipeline:

```text
curl
 │
 ▼
multipart/form-data
 │
 ▼
FastAPI
 │
 ├── query → Form
 ├── project_id → Form
 └── image → File
 │
 ▼
Pydantic DTO + UploadFile
 │
 ▼
Handler
 │
 ▼
HumanMessage
 │
 ├── text
 └── image
 │
 ▼
LangGraph State
 │
 ▼
image_router
 │
 ├── image → normal_llm_agent
 │
 └── no image → query_type_decider
 │
 ▼
MessagesPlaceholder
 │
 ▼
Multimodal LLM
 │
 ▼
Streaming response
 │
 ▼
Client
```

The most important architectural idea is:

> **FastAPI handles the HTTP request, the handler converts the request into LangChain messages, and LangGraph controls how those messages move through the application.**

This separation allows the same graph and LLM logic to work with both normal text conversations and multimodal conversations.
