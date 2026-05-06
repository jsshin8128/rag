# RAG 파이프라인 실습 환경 설정 가이드

> 처음 설정할 때 한 번만 따라하면 됩니다. 천천히 읽으면서 순서대로 진행해주세요!

---

## 시작 전 확인사항

### Python 버전 확인

터미널(명령 프롬프트)을 열고 아래 명령어를 입력하세요.

```bash
python3 --version
```

**Python 3.10 이상**이어야 합니다. 버전이 낮다면 [python.org](https://www.python.org/downloads/)에서 최신 버전을 설치해주세요.

> 💡 **터미널이 처음이라면?**
>
> - Mac: `Cmd + Space` → "터미널" 검색
> - Windows: `Win + R` → `cmd` 입력 → 확인

---

## Step 1. 프로젝트 폴더로 이동

제공한 프로젝트 폴더(rag)를 받았다면, 터미널에서 해당 폴더로 이동합니다.

```bash
cd ~/rag
```

> 💡 `cd`는 "Change Directory"의 약자로, 폴더를 이동하는 명령어입니다.

잘 이동했는지 확인하려면:

```bash
ls
```

`api`, `frontend`, `data`, `requirements.txt` 등이 보이면 정상입니다.

---

## Step 2. 가상환경 만들기

가상환경은 **이 프로젝트에서만 쓸 패키지들을 담는 별도 공간**입니다.
다른 프로젝트와 패키지가 섞이지 않도록 해줘요.

```bash
python3 -m venv .venv
```

> 💡 명령어를 실행하면 `.venv` 폴더가 생깁니다. 잠깐 기다려주세요.

---

## Step 3. 가상환경 활성화

가상환경을 만들었으면 **활성화**해야 합니다. 운영체제에 맞는 명령어를 입력하세요.

**Mac / Linux**

```bash
source .venv/bin/activate
```

**Windows (명령 프롬프트)**

```bash
.venv\Scripts\activate
```

**Windows (PowerShell)**

```bash
.venv\Scripts\Activate.ps1
```

✅ 성공하면 터미널 왼쪽에 `(.venv)` 표시가 나타납니다.

```
(.venv) user@computer:~/rag$
```

> ⚠️ 터미널을 새로 열 때마다 가상환경을 다시 활성화해야 합니다!

---

## Step 4. 패키지 설치

이 프로젝트에 필요한 라이브러리들을 한 번에 설치합니다.

```bash
pip install -r requirements.txt
```

> 💡 `requirements.txt`에 적힌 패키지 목록을 자동으로 설치해줍니다.
> 인터넷 연결이 필요하며, 수 분 정도 걸릴 수 있어요.

설치가 완료되면 아래 명령어로 확인할 수 있습니다.

```bash
pip list
```

`langchain`, `streamlit`, `chromadb` 등이 보이면 성공입니다.

---

## Step 5. API 키 설정

OpenAI API 키를 설정해야 AI 기능이 작동합니다.

**1. 설정 파일 복사**

```bash
cp .env.example .env
```

**2. `.env` 파일 열기**

메모장이나 VS Code로 `.env` 파일을 열고, `sk-...` 부분을 강사에게 받은 실제 API 키로 교체합니다.

```
OPENAI_API_KEY=sk-여기에_실제_API_키를_입력하세요
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_DB_PATH=./chroma_db
DATA_DIR=./data
API_PORT=8000
```

> ⚠️ API 키는 절대 외부에 공유하지 마세요! `.gitignore`에 등록되어 있어 Git에는 올라가지 않습니다.

---

## Step 6. 서버 실행

터미널 창을 **2개** 열어야 합니다. (API 서버용, Streamlit용)

### 터미널 1 — API 서버 실행

```bash
cd ~/rag/api
source ../.venv/bin/activate    # 가상환경 활성화 (Mac/Linux)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

아래 메시지가 뜨면 성공입니다.

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 터미널 2 — Streamlit 실행

```bash
cd ~/rag
source .venv/bin/activate       # 가상환경 활성화 (Mac/Linux)
.venv/bin/streamlit run frontend/app.py --server.port 8501
```

아래 메시지가 뜨면 성공입니다.

```
  Local URL: http://localhost:8501
```

브라우저가 자동으로 열리거나, 직접 [http://localhost:8501](http://localhost:8501) 을 열어주세요.

---

## 접속 주소 정리


| 서비스    | 주소                                                       | 설명        |
| ------ | -------------------------------------------------------- | --------- |
| 실습 UI  | [http://localhost:8501](http://localhost:8501)           | 여기서 실습합니다 |
| API 서버 | [http://localhost:8000](http://localhost:8000)           | 백엔드 서버    |
| API 문서 | [http://localhost:8000/docs](http://localhost:8000/docs) | API 목록 확인 |


---

## 자주 발생하는 오류

### `(.venv)` 표시가 안 보여요

→ 가상환경이 활성화되지 않은 것입니다. Step 3을 다시 실행하세요.

### `ModuleNotFoundError` 가 뜨면

→ 패키지가 설치되지 않은 것입니다. Step 4를 다시 실행하세요.

### API 서버가 `미연결` 상태로 뜨면

→ 터미널 1에서 API 서버가 실행 중인지 확인하세요.

### `OPENAI_API_KEY` 관련 오류가 뜨면

→ `.env` 파일에 API 키가 올바르게 입력됐는지 확인하세요.

### `인덱싱 실패` 오류가 뜨면

→ API 키가 유효한지, 인터넷 연결이 되어 있는지 확인하세요.