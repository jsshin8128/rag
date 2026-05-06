import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document


def get_embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )


def embed_and_store(
    chunks: list[dict],
    chroma_path: str = "./chroma_db",
    collection_name: str = "rag_workshop",
) -> dict:
    """Embed chunks and store in ChromaDB. Returns store metadata."""
    # 기존 컬렉션 삭제 후 재생성 → 중복 방지
    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    embedding_model = get_embedding_model()

    docs = [
        Document(page_content=c["content"], metadata={"source": c["source"], "chunk_id": c["chunk_id"]})
        for c in chunks
    ]

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=chroma_path,
        collection_name=collection_name,
    )

    sample_vector = embedding_model.embed_query(chunks[0]["content"]) if chunks else []

    return {
        "total_chunks_stored": len(chunks),
        "collection_name": collection_name,
        "chroma_path": chroma_path,
        "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        "vector_dimensions": len(sample_vector),
        "sample_vector_preview": sample_vector[:8] if sample_vector else [],
    }


def load_vectorstore(
    chroma_path: str = "./chroma_db",
    collection_name: str = "rag_workshop",
) -> Chroma:
    """Load existing vectorstore from disk."""
    return Chroma(
        persist_directory=chroma_path,
        embedding_function=get_embedding_model(),
        collection_name=collection_name,
    )
