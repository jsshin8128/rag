#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV="$SCRIPT_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"
UVICORN="$VENV/bin/uvicorn"
STREAMLIT="$VENV/bin/streamlit"

echo "=================================="
echo " RAG 워크샵 — 시작 스크립트"
echo "=================================="

# 가상환경 확인
if [ ! -f "$PYTHON" ]; then
  echo "[!] 가상환경이 없습니다. 생성 중..."
  python3 -m venv "$VENV"
fi

# .env 확인
if [ ! -f .env ]; then
  echo "[!] .env 파일이 없습니다. .env.example을 복사합니다."
  cp .env.example .env
  echo "[!] .env 파일에 OPENAI_API_KEY를 입력한 후 다시 실행하세요."
  exit 1
fi

# 패키지 설치
echo "[1/3] 패키지 설치 중..."
"$PIP" install -q -r requirements.txt

# 사전 인덱싱
echo "[2/3] 사전 인덱싱 (문서 임베딩)..."
"$PYTHON" preprocess.py

# 서버 실행
echo "[3/3] 서버 실행..."
echo ""
echo "  API 서버: http://localhost:8000"
echo "  Streamlit: http://localhost:8501"
echo ""

# API 서버 백그라운드 실행
cd api && "$UVICORN" main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
cd "$SCRIPT_DIR"

sleep 2

# Streamlit 실행 (포그라운드)
"$STREAMLIT" run frontend/app.py --server.port 8501

# 종료 시 API도 종료
kill $API_PID 2>/dev/null || true
