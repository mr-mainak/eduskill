from pymongo import MongoClient
from bson import ObjectId
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pickle


# 🔹 Global embedding cache
embedding_model = None


def get_embedding_function():
    global embedding_model

    if embedding_model is None:
        model_name = "nomic-embed-text:latest"
        embedding_model = OllamaEmbeddings(model=model_name, num_gpu=1, keep_alive=0 )
        print("✅ Ollama Embedding Model Loaded")
    else:
        print("⚡ Using Cached Embedding Model")

    return embedding_model


# 🔹 Word-based chunking
def split_by_words(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += chunk_size - overlap

    return chunks


# 🔹 MongoDB Loader
def load_documents_from_mongodb(uri, db_name, collection_name, ids=None):
    client = MongoClient(uri)
    collection = client[db_name][collection_name]


     # ✅ Only required fields (IMPORTANT)
    cursor = collection.find({}, {
        "_id": 1,
        "description": 1,
        "title": 1,
        "class": 1,
        "type": 1,
        "subtype": 1
    })

    # query = {}
    # if ids:
    #     query["_id"] = {"$in": [ObjectId(i) for i in ids]}

    # cursor = collection.find(query)


    documents = []

    for doc in cursor:
        description = doc.get("description", "").strip()
        if not description:
            continue

        word_count = len(description.split())

        metadata = {
            "id": str(doc["_id"]),
            "title": doc.get("title"),
            "class": doc.get("class"),
            "type": doc.get("type"),
            "subtype": doc.get("subtype"),
        }

        # ✅ Conditional chunking
        if word_count > 500:
            chunks = split_by_words(description, 500, 100)

            for i, chunk in enumerate(chunks):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={**metadata, "chunk_id": i}
                    )
                )
        else:
            documents.append(
                Document(
                    page_content=description,
                    metadata=metadata
                )    
            )
        print(f"Processed docs: {len(documents)}")
        for d in documents:
            print(f"📌 doc_id: {d.metadata['id']}")
        # print(documents)    

    return documents
    


# 🔹 Main
if __name__ == "__main__":

    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "eduskill"
    COLLECTION_NAME = "projects"

    SAVE_PATH = "./faiss_index"

    docs = load_documents_from_mongodb(
        uri=MONGO_URI,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME
    )

    if not docs:
        print("⚠️ No documents found")
        exit()

    embedding_fn = get_embedding_function()

    # 🔹 Create FAISS index
    db = FAISS.from_documents(docs, embedding_fn)

    # 🔹 Save locally (IMPORTANT for production)
    db.save_local(SAVE_PATH)

    print(f"✅ Stored {len(docs)} documents in FAISS at `{SAVE_PATH}`")