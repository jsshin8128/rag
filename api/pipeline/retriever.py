from langchain_chroma import Chroma
from .embedder import load_vectorstore


def retrieve(
    query: str,
    top_k: int = 3,
    chroma_path: str = "./chroma_db",
    collection_name: str = "rag_workshop",
) -> dict:
    """Search vectorstore and return top-k relevant chunks with scores."""
    vectorstore: Chroma = load_vectorstore(chroma_path, collection_name)

    results_with_scores = vectorstore.similarity_search_with_relevance_scores(
        query, k=top_k
    )

    retrieved = []
    for rank, (doc, score) in enumerate(results_with_scores, start=1):
        retrieved.append({
            "rank": rank,
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "similarity_score": round(score, 4),
        })

    return {
        "query": query,
        "top_k": top_k,
        "results": retrieved,
    }
