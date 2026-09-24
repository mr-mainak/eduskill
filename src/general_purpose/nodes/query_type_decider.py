from src.general_purpose.states.agent_state import GeneralPurposeState
from utils.config_reader import load_config
from utils.prompt_reader import load_prompt
from src.general_purpose.models.query_type_decider import QueryType
from utils.logger import global_logger
from utils.filter_message import filter_tool_messages
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.types import Command
import sys


def query_type_decider_node(state: GeneralPurposeState) -> Command[Literal["semantic_search_agent", "normal_llm_agent"]]:
    """
    Determines the next agent to handle a query based on the current teaching assistant agent state.

    This function uses a language model to analyze the user's question and relevant context,
    then decides whether to route the query to a semantic search agent or a textbook content extractor agent.

    Args:
        state (TeachingAssistantAgentState): The current state of the teaching assistant agent, 
            containing the user's messages, class number, and subject name.

    Returns:
        Command[Literal["semantic_search_agent", "textbook_content_extractor_agent"]]: 
            A command indicating which agent should handle the query next.

    Raises:
        SystemExit: If an exception occurs during processing.
    """
    try:
        prompt = ChatPromptTemplate.from_template(load_prompt("./prompts/query_type_decider_agent_prompt.txt"))

        llm_model = ChatOllama(**load_config("./config/query_type_decider_agent_config.json"))

        llm = llm_model.with_structured_output(QueryType)

        chain = prompt | llm

        # filtered_messages = filter_tool_messages(state["messages"])

        response = chain.invoke({
            "question": state["messages"][-1],
        })

        print(Command(
            goto=response.next_agent
        ))

        return Command(
            goto=response.next_agent
        )
    
    except Exception as e:
        global_logger.error(f"Error in query_type_decider_node: {e}")
        # sys.exit(1)