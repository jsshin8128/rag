from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> list[dict]:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    langchain_docs = [
        Document(page_content=doc["content"], metadata={"source": doc["filename"]})
        for doc in documents
    ]

    split_docs = splitter.split_documents(langchain_docs)

    chunks = []
    for i, doc in enumerate(split_docs):
        chunks.append({
            "chunk_id": i,
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "char_count": len(doc.page_content),
        })

    return chunks
