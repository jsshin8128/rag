"""
사전 인덱싱 스크립트
실습 전 한 번만 실행하면 됩니다: python preprocess.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "api"))

from pipeline.loader import load_documents
from pipeline.chunker import chunk_documents
from pipeline.embedder import embed_and_store

DATA_DIR = os.getenv("DATA_DIR", "./data")
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def main():
    print("=" * 50)
    print("RAG 워크샵 — 사전 인덱싱")
    print("=" * 50)

    print(f"\n[1/3] 문서 로딩 중... ({DATA_DIR})")
    docs = load_documents(DATA_DIR)
    if not docs:
        print(f"오류: {DATA_DIR} 에 .txt 파일이 없습니다.")
        sys.exit(1)
    for d in docs:
        print(f"  ✓ {d['filename']} ({d['char_count']:,}자)")

    print(f"\n[2/3] 청킹 중... (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    chunks = chunk_documents(docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    print(f"  ✓ {len(chunks)}개 청크 생성됨")

    print(f"\n[3/3] 임베딩 & ChromaDB 저장 중... ({CHROMA_PATH})")
    result = embed_and_store(chunks, chroma_path=CHROMA_PATH)
    print(f"  ✓ {result['total_chunks_stored']}개 청크 저장 완료")
    print(f"  ✓ 벡터 차원: {result['vector_dimensions']}")
    print(f"  ✓ 모델: {result['embedding_model']}")

    print("\n✅ 사전 인덱싱 완료! 이제 API 서버와 Streamlit을 실행하세요.")
    print("   API:  cd api && uvicorn main:app --reload --port 8000")
    print("   UI:   streamlit run frontend/app.py")


if __name__ == "__main__":
    main()
