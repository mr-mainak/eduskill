from src.general_purpose.states.agent_state import GeneralPurposeState
from src.general_purpose.tools.semantic_search import search_textbook_by_semantics
from utils.mongo_context_retriever import read_project
from utils.config_reader import load_config
from utils.logger import global_logger
from utils.prompt_reader import load_prompt
from utils.filter_message import filter_tool_messages
from utils.extract_text_from_message import extract_text_from_message
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import sys


def semantic_search_node(state: GeneralPurposeState) -> GeneralPurposeState:
    try:
        prompt = ChatPromptTemplate.from_template(load_prompt("./prompts/semantic_search_agent_prompt_whole_context.txt"))

        project_id = state["project_id"]

        config = load_config("./config/semantic_search_agent_config.json")
        context = read_project(project_id=project_id)

        # if state["subject_name"].lower() == "mathematics":
        #     config["model"] = "qwen3:14b"

        llm_model = ChatOllama(**config)
        # llm = llm_model.bind_tools([search_textbook_by_semantics])
        chain = prompt | llm_model

        filtered_messages = filter_tool_messages(state["messages"])
        # filtered_messages = state["messages"]
        # print(filtered_messages)

        #Extract only text part no image
        recent_messages = filtered_messages[-7:]
        question = "\n\n".join(extract_text_from_message(msg)
            for msg in recent_messages
            if extract_text_from_message(msg))
        # print("question::::::::::::::::::",question)

        return {
            "messages": [chain.invoke({
                    "question": question,
                    "project_id": project_id,
                    "context": context
                })],
            "caller": "semantic_search_agent"
        }
    
    except Exception as e:
        global_logger.error(f"Error in semantic_search_node: {e}")
        # sys.exit(1)