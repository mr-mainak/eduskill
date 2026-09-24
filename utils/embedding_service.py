from langchain_huggingface import HuggingFaceEmbeddings

from langchain_ollama import OllamaEmbeddings

import torch
 
 
embedding_model = None
 
 
def get_embedding_model() -> OllamaEmbeddings:

    """

    Returns a cached instance of a HuggingFace embedding model.
 
    Loads the model only once and caches it for future use to improve performance and avoid

    repeated loading. If the model is already loaded, it reuses the cached instance.
 
    Returns:

        HuggingFaceEmbeddings: The loaded embedding model.
 
    Notes:

        - Uses the "nomic-ai/nomic-embed-text-v1.5" model.

        - Loads the model on the CUDA device.

        - Normalization of embeddings is disabled.

    """

    global embedding_model
 
    # Load the model only once to avoid repeated loading

    if embedding_model is None:

        # model_name = "nomic-ai/nomic-embed-text-v1.5"

        # model_name = "infly/inf-retriever-v1"

        # model_kwargs = {'device': 'cuda', 'trust_remote_code': True}

        # model_kwargs = {'trust_remote_code': True}

        # encode_kwargs = {'normalize_embeddings': False}
 
        # Initialize the HuggingFaceEmbeddings model

        # embeddings = HuggingFaceEmbeddings(

        #    model_name=model_name,

        #    model_kwargs=model_kwargs,

        #    encode_kwargs=encode_kwargs

        # )

        embeddings = OllamaEmbeddings(

            model="nomic-embed-text:latest",

            num_gpu=24,

            keep_alive=0

        )

        embedding_model = embeddings

        print("Model Loaded and Cached!")

    else:

        print("Using Cached Embedding Model.")
 
    return embedding_model
 
 
def clear_embedding_model_cache() -> None:

    """

    Clears the cached embedding model and frees GPU memory.
 
    This function deletes the in-memory embedding model and manually clears

    the CUDA memory cache using `torch.cuda.empty_cache()` to release resources.

    Useful when the model is no longer needed or memory must be freed.

    """

    global embedding_model

    if embedding_model:

        del embedding_model  # Delete the cached model

        embedding_model = None

        torch.cuda.empty_cache()  # Free up GPU memory

        print("Embedding Model cache cleared.")
 