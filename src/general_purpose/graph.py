from src.general_purpose.states.agent_state import GeneralPurposeState
from src.general_purpose.nodes.semantic_search import semantic_search_node
from src.general_purpose.nodes.normal_llm import normal_llm_search_node
from src.general_purpose.nodes.query_type_decider import query_type_decider_node
from src.general_purpose.nodes.image_router import image_router_node
from src.general_purpose.nodes.tool_executor import should_call_tool_executor, tool_executor
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver


def create_general_purpose_graph() -> CompiledStateGraph[GeneralPurposeState, None, GeneralPurposeState, GeneralPurposeState]:

    graph_builder = StateGraph(GeneralPurposeState)

    graph_builder.add_node("image_router", image_router_node)
    graph_builder.add_node("query_type_decider", query_type_decider_node)
    graph_builder.add_node("semantic_search_agent", semantic_search_node)
    graph_builder.add_node("normal_llm_agent", normal_llm_search_node)
    graph_builder.add_node("tool_executor", tool_executor)


    # graph_builder.add_edge(START, "query_type_decider")
    graph_builder.add_edge(START,"image_router")

    graph_builder.add_conditional_edges("semantic_search_agent",
                                        should_call_tool_executor, 
                                        {True: "tool_executor", False: END})

    graph_builder.add_conditional_edges("normal_llm_agent",
                                        should_call_tool_executor, 
                                        {True: "tool_executor", False: END})
    
    # graph_builder.add_edge("message_filter_node", END)
    
    
    checkpointer = MemorySaver()
    
    return graph_builder.compile(checkpointer=checkpointer)
    # return graph_builder.compile()