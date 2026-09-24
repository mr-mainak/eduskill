from typing import Literal
from langgraph.types import Command
from src.general_purpose.states.agent_state import GeneralPurposeState


def image_router_node(state: GeneralPurposeState) -> Command[Literal["query_type_decider", "normal_llm_agent"]]:

    if state.get("image") is not None:
        return Command(goto="normal_llm_agent")

    return Command(goto="query_type_decider")