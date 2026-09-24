from utils.embedding_service import get_embedding_model
from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever
 
 
def get_retriever(project_id: str) -> BaseRetriever:
    """
    Loads a FAISS vector store from disk and returns a configured retriever.
 
    Args:
        id (str): The ID of the document to retrieve.
 
    Returns:
        BaseRetriever: A retriever object using Maximal Marginal Relevance (MMR) for search.
 
    Notes:
        - The FAISS store is loaded from './faiss_index'.
        - Uses the cached HuggingFace embedding model.
        - Search type is set to "mmr" with k=1 (returns the single most relevant document).
        - `allow_dangerous_deserialization=True` is enabled, which can be a security risk—
          ensure trusted data only.
    """
    db = FAISS.load_local(
        folder_path=f"./faiss_index",
        embeddings=get_embedding_model(),
        allow_dangerous_deserialization=True
    )

    print("loaded_db")

    all_docs = list(db.docstore._dict.values())

    print(f"Total stored docs: {len(all_docs)}")

    # for doc in all_docs[:30]:
    #     print(doc.metadata)
 
    retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3,         
                        "filter": {"id": project_id} } )
 
    return retriever


# if __name__ == "__main__":

#     retriever = get_retriever("6a43bdc0ac9539fbe50f3d82")
#     docs=retriever.invoke("How does the Smart Torch work?") 
#     print(docs)
    # for doc in docs:     
    #     print(doc.metadata)     
    #     print(doc.page_content)
    
    