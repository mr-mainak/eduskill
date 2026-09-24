from utils.retriever import get_retriever
from langchain_core.documents import Document
from langchain_core.tools import tool


@tool
def search_textbook_by_semantics(project_id: str, query: str) -> list[Document]:
    """
    Search for relevant documents in a specific FAISS vector collection using semantic similarity.

    Args:
        project_name (str): Name of the vector store collection (e.g., "6a43bdc0ac9539fbe50f3d82") corresponding to a specific project.
        query (str): Natural language query from the user to search for in the vector store.

    Returns:
        list[Document]: A list of LangChain `Document` objects matching the query along with metadata.

    Example:
        search_knowledge_base(
            collection_name="6a43bdc0ac9539fbe50f3d82",
            query="how do butterflies grow",
        )

    Note:
        The function uses semantic similarity.
    """
    retriver = get_retriever(project_id=project_id)
    docs = retriver.invoke(query)
    print(docs)
    return docs