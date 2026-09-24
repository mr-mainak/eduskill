import base64

from src.general_purpose.states.agent_state import GeneralPurposeState
from src.general_purpose.tools.date_time import get_current_time_and_date
from utils.config_reader import load_config
from utils.logger import global_logger
from utils.prompt_reader import load_prompt
from utils.filter_message import filter_tool_messages

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama


from src.general_purpose.states.agent_state import GeneralPurposeState
from src.general_purpose.tools.date_time import get_current_time_and_date
from utils.config_reader import load_config
from utils.logger import global_logger
from utils.prompt_reader import load_prompt
from utils.filter_message import filter_tool_messages

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

def normal_llm_search_node(state: GeneralPurposeState) -> GeneralPurposeState:

    try:
        # System prompt
        system_prompt = load_prompt("./prompts/normal_llm_search_agent_prompt.txt")

        # Create chat prompt:
        # 1. System instructions
        # 2. Actual conversation messages
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # Load Ollama configuration
        config = load_config("./config/normal_llm_agent_config.json")

        llm_model = ChatOllama(**config)

        # Bind tools
        llm = llm_model.bind_tools([get_current_time_and_date])

        chain = prompt | llm

        # Preserve HumanMessage / AIMessage content,
        # including multimodal image blocks.
        filtered_messages = filter_tool_messages(state["messages"])

        messages = filtered_messages[-7:]

        # print("Messages sent to LLM:")
        # print(messages)

        response = chain.invoke({"messages": messages})

        return {
            "messages": [response],
            "caller": "normal_llm_agent",
        }

    except Exception as e:

        global_logger.error(
            f"Error in normal_llm_search_node: {e}"
        )

        return {
            "messages": [],
            "caller": "normal_llm_agent",
        }