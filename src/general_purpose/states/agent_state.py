from typing import Annotated, Optional
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class GeneralPurposeState(TypedDict):
    messages: Annotated[list, add_messages]
    project_id: str
    caller: str
    image: Optional[dict]