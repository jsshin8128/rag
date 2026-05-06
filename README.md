## 빠른 시작

### 한 번에 실행 (권장)
```bash
bash start.sh
```
가상환경 설치 → 패키지 설치 → 사전 인덱싱 → API + Streamlit 동시 실행

---

### 수동 실행

**1. API 서버**
```bash
# ~/rag 에서 실행
cd ~/rag/api && ~/rag/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

**2. Streamlit 클라이언트** (새 터미널)
```bash
# ~/rag 에서 실행
cd ~/rag && .venv/bin/streamlit run frontend/app.py --server.port 8501
```

| 서비스 | 주소 |
|--------|------|
| Streamlit UI | http://localhost:8501 |
| API 서버 | http://localhost:8000 |
| API 문서 | http://localhost:8000/docs |

---

## 사전 준비

```bash
# 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화 (~/rag 에서 실행)
source ~/rag/.venv/bin/activate  # Mac / Linux
~/rag/.venv/Scripts/activate     # Windows

# 패키지 설치
pip install -r requirements.txt

# .env 설정
cp .env.example .env
# .env 에 OPENAI_API_KEY 입력
```
