from src.general_purpose.states.agent_state import GeneralPurposeState
from src.general_purpose.tools.date_time import get_current_time_and_date
from src.general_purpose.tools.semantic_search import search_textbook_by_semantics
# from src.utils.logger import global_logger
from typing import Literal
from langchain_core.messages import ToolMessage
from langgraph.types import Command
import sys


all_tools = [
    search_textbook_by_semantics, 
    get_current_time_and_date
    ]

tools_dict = {t.name: t for t in all_tools}


def should_call_tool_executor(state: GeneralPurposeState) -> bool:
    """Check if the last message contains tool calls."""
    result = state["messages"][-1]
    return hasattr(result, "tool_calls") and len(result.tool_calls) > 0


def tool_executor(state: GeneralPurposeState) -> Command[Literal["semantic_search_agent", "normal_llm_agent"]]:
    try:
        tool_calls = state["messages"][-1].tool_calls
        results = []
        # output_page_number = []

        for t in tool_calls:
            tool_name = t['name']

            if tool_name not in tools_dict:
                result = "Invalid tool name"
                
            else:
                result = tools_dict[tool_name].invoke(t['args'])

                # if state["caller"] == "semantic_search_agent" and result:
                #     output_page_number = result[0].metadata.get("page", None)

                # elif state["caller"] == "textbook_content_extractor_agent" and tool_name == "extract_textbook_content_by_metadata":
                #     output_page_number = result[0].get("page", None)

            results.append(ToolMessage(tool_call_id=t['id'], name=tool_name, content=str(result)))

        # return Command(
        #     update={"messages": results, "output_page_number": output_page_number},
        #     goto=state["caller"]
        # )
        return Command(
                    update={"messages": results},
                    goto=state["caller"]
                )
    
    except Exception as e:
        global_logger.error(f"Error in tool_executor: {e}")
        # sys.exit(1)