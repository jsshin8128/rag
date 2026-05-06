import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# api/ 한 단계 위가 프로젝트 루트 → 어디서 uvicorn을 실행해도 경로 고정
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from pipeline.loader import load_documents
from pipeline.chunker import chunk_documents
from pipeline.embedder import embed_and_store
from pipeline.retriever import retrieve
from pipeline.generator import generate, PROMPT_STYLES
from pipeline.evaluator import evaluate

def _resolve(env_key: str, default_rel: str) -> str:
    val = os.getenv(env_key, default_rel)
    p = Path(val)
    return str(p if p.is_absolute() else PROJECT_ROOT / p)

DATA_DIR   = _resolve("DATA_DIR",       "data")
CHROMA_PATH = _resolve("CHROMA_DB_PATH", "chroma_db")
COLLECTION = "rag_workshop"

app = FastAPI(title="RAG Workshop API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response models ──────────────────────────────────────────────────

class ChunkRequest(BaseModel):
    chunk_size: int = Field(300, ge=50, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(3, ge=1, le=10)
    chunk_size: int = Field(300, ge=50, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)
    prompt_style: str = "기본"

class FullPipelineRequest(BaseModel):
    query: str
    top_k: int = Field(3, ge=1, le=10)
    prompt_style: str = "기본"


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/load")
def api_load():
    """Step 1: Load raw documents."""
    docs = load_documents(DATA_DIR)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No .txt files found in {DATA_DIR}")
    return {"step": "load", "documents": docs}


@app.post("/chunk")
def api_chunk(req: ChunkRequest):
    """Step 2: Chunk documents."""
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs, chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
    return {
        "step": "chunk",
        "chunk_size": req.chunk_size,
        "chunk_overlap": req.chunk_overlap,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }


@app.post("/embed")
def api_embed(req: ChunkRequest):
    """Step 3+4: Embed chunks and store in ChromaDB."""
    try:
        docs = load_documents(DATA_DIR)
        if not docs:
            raise HTTPException(status_code=404, detail=f"데이터 없음: {DATA_DIR} 에 .txt 파일을 추가하세요.")
        chunks = chunk_documents(docs, chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
        result = embed_and_store(chunks, chroma_path=CHROMA_PATH, collection_name=COLLECTION)
        return {"step": "embed_and_store", **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱싱 실패: {e}")


@app.post("/retrieve")
def api_retrieve(req: QueryRequest):
    """Step 5: Retrieve top-k relevant chunks."""
    chroma_path = Path(CHROMA_PATH)
    if not chroma_path.exists() or not any(chroma_path.iterdir()):
        raise HTTPException(status_code=400, detail="ChromaDB가 비어있습니다. /embed를 먼저 실행하세요.")
    result = retrieve(req.query, top_k=req.top_k, chroma_path=CHROMA_PATH, collection_name=COLLECTION)
    return {"step": "retrieve", **result}


@app.post("/generate")
def api_generate(req: QueryRequest):
    """Step 6+7: Retrieve then generate answer."""
    retrieval = retrieve(req.query, top_k=req.top_k, chroma_path=CHROMA_PATH, collection_name=COLLECTION)
    generation = generate(req.query, retrieval["results"], prompt_style=req.prompt_style)
    return {
        "step": "generate",
        "retrieved": retrieval["results"],
        **generation,
    }


@app.post("/pipeline")
def api_full_pipeline(req: FullPipelineRequest):
    """Run full RAG pipeline: retrieve → generate → evaluate."""
    retrieval = retrieve(req.query, top_k=req.top_k, chroma_path=CHROMA_PATH, collection_name=COLLECTION)
    generation = generate(req.query, retrieval["results"], prompt_style=req.prompt_style)
    evaluation = evaluate(req.query, retrieval["results"], generation["answer"])

    return {
        "query": req.query,
        "retrieved": retrieval["results"],
        "full_prompt": generation["full_prompt"],
        "system_prompt": generation["system_prompt"],
        "answer": generation["answer"],
        "model": generation["model"],
        "evaluation": evaluation,
        "token_usage": {
            "prompt_tokens": generation["prompt_tokens"],
            "completion_tokens": generation["completion_tokens"],
        },
    }


@app.get("/embed/status")
def api_embed_status():
    """ChromaDB 컬렉션에 실제 문서가 있는지 확인."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_collection(COLLECTION)
        has_data = collection.count() > 0
    except Exception:
        has_data = False
    return {"indexed": has_data}


@app.delete("/embed")
def api_clear_embed():
    """ChromaDB 컬렉션 삭제 (파일은 유지, 연결 캐시 충돌 방지)."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    return {"status": "cleared"}


@app.get("/prompt-styles")
def api_prompt_styles():
    return {"styles": list(PROMPT_STYLES.keys())}
