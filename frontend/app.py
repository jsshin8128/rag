import base64
from pathlib import Path
import streamlit as st
import requests

API_BASE = "http://localhost:8000"

def _logo_b64() -> str:
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    return base64.b64encode(logo_path.read_bytes()).decode()

st.set_page_config(
    page_title="RAG 파이프라인 이해하기",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Toss Design System CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

/* 전체 배경 */
.stApp { background: #F2F4F6; }
html, body, [class*="css"], * { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important; }

/* 사이드바 */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5E8EB;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }

/* 메인 패딩 */
.main .block-container { padding: 2rem 2rem 4rem 2rem; max-width: 900px; }

/* 버튼 - 기본(primary) */
.stButton > button {
    background: #0064FF;
    color: #fff;
    border: none;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    padding: 0.65rem 1.2rem;
    transition: background 0.15s;
    width: 100%;
}
.stButton > button:hover { background: #0051CC; color: #fff; border: none; }
.stButton > button:active { background: #003D99; }

/* 추천 질문 카드 버튼 (secondary) */
section[data-testid="stMain"] div[data-testid="stButton"] > button[kind="secondary"] {
    background: #fff !important;
    color: #191F28 !important;
    border: 1px solid #E5E8EB !important;
    border-radius: 14px !important;
    text-align: left !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 14px 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    transition: background 0.15s, border-color 0.15s !important;
}
section[data-testid="stMain"] div[data-testid="stButton"] > button[kind="secondary"]::after {
    content: '›';
    color: #B0B8C1;
    font-size: 1.1rem;
    flex-shrink: 0;
}
section[data-testid="stMain"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #F8FBFF !important;
    border-color: #C9DCFF !important;
    color: #191F28 !important;
}

/* 텍스트 인풋 */
.stTextInput > div > div > input {
    background: #fff;
    border: 1.5px solid #E5E8EB;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    color: #191F28;
    box-shadow: none;
}
.stTextInput > div > div > input:focus {
    border-color: #0064FF;
    box-shadow: 0 0 0 3px rgba(0,100,255,0.1);
}

/* 슬라이더 */
.stSlider > div > div > div > div { background: #0064FF; }

/* 셀렉트박스 */
.stSelectbox > div > div {
    background: #fff;
    border: 1.5px solid #E5E8EB;
    border-radius: 12px;
}

/* Expander 제거 → 커스텀 카드 사용 */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border: none !important;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 0.75rem;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    font-size: 0.95rem;
    color: #191F28;
    padding: 1rem 1.25rem;
}
[data-testid="stExpander"] summary:hover { background: #F8F9FA; }

/* 메트릭 */
[data-testid="stMetric"] {
    background: #F8F9FA;
    border-radius: 12px;
    padding: 0.75rem 1rem;
}
[data-testid="stMetricLabel"] { font-size: 0.78rem; color: #6B7684; font-weight: 500; }
[data-testid="stMetricValue"] { font-size: 1.3rem; font-weight: 700; color: #191F28; }

/* 구분선 */
hr { border-color: #E5E8EB; margin: 1rem 0; }

/* 알림 박스 */
.stSuccess { border-radius: 12px; }
.stWarning { border-radius: 12px; }
.stError   { border-radius: 12px; }
.stInfo    { border-radius: 12px; }

/* progress bar */
.stProgress > div > div { background: #0064FF; border-radius: 99px; }
.stProgress > div { background: #E5E8EB; border-radius: 99px; }

/* 텍스트에리어 */
.stTextArea textarea {
    background: #F8F9FA;
    border: 1.5px solid #E5E8EB;
    border-radius: 12px;
    font-family: 'Pretendard', monospace;
    font-size: 0.85rem;
    color: #191F28;
}

/* ── 커스텀 컴포넌트 ── */
.toss-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 0.25rem;
}
.toss-logo-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: #0064FF; display: inline-block;
}
.toss-title {
    font-size: 1.5rem; font-weight: 700; color: #191F28; margin: 0;
}
.toss-subtitle { font-size: 0.88rem; color: #6B7684; margin-bottom: 1.75rem; }

.toss-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

.step-row { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 1rem; }
.step-badge {
    min-width: 28px; height: 28px;
    background: #0064FF; color: #fff;
    border-radius: 50%; font-size: 0.8rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
}
.step-badge.done { background: #00C471; }
.step-badge.muted { background: #B0B8C1; }
.step-title { font-size: 1rem; font-weight: 700; color: #191F28; }
.step-sub   { font-size: 0.8rem; color: #6B7684; margin-top: 2px; }

.chunk-pill {
    background: #F2F4F6;
    border-left: 3px solid #0064FF;
    border-radius: 0 10px 10px 0;
    padding: 8px 12px;
    margin: 6px 0;
    font-size: 0.83rem;
    color: #191F28;
    white-space: pre-wrap;
    line-height: 1.55;
}
.chunk-meta { font-size: 0.75rem; color: #6B7684; margin-bottom: 3px; font-weight: 500; }

.score-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.65rem 0;
    border-bottom: 1px solid #F2F4F6;
}
.score-row:last-child { border-bottom: none; }
.score-label { font-size: 0.88rem; color: #6B7684; font-weight: 500; flex: 1; }
.score-val   { font-size: 1.05rem; font-weight: 700; width: 48px; text-align: right; }
.score-bar-wrap { width: 120px; background: #E5E8EB; border-radius: 99px; height: 6px; margin: 0 14px; }
.score-bar-fill  { height: 6px; border-radius: 99px; }
.c-green { color: #00C471; } .c-orange { color: #FF9500; } .c-red { color: #FF3B30; }
.bg-green { background: #00C471; } .bg-orange { background: #FF9500; } .bg-red { background: #FF3B30; }

.sim-badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 99px; font-size: 0.75rem; font-weight: 600;
    margin-left: 8px;
}
.sim-high { background: #E8FBF0; color: #00C471; }
.sim-mid  { background: #FFF5E6; color: #FF9500; }
.sim-low  { background: #FFEDED; color: #FF3B30; }

.answer-box {
    background: #F2F8FF;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-size: 0.92rem;
    color: #191F28;
    line-height: 1.7;
    white-space: pre-wrap;
}
.tag {
    display: inline-block; padding: 2px 10px;
    border-radius: 99px; font-size: 0.75rem; font-weight: 600;
}
.tag-blue   { background: #E6F0FF; color: #0064FF; }
.tag-gray   { background: #F2F4F6; color: #6B7684; }
.tag-green  { background: #E8FBF0; color: #00C471; }

.sidebar-section { margin-bottom: 1.5rem; }
.sidebar-label {
    font-size: 0.75rem; font-weight: 700; color: #B0B8C1;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}
.api-dot {
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block; margin-right: 6px;
}
.api-on  { background: #00C471; }
.api-off { background: #FF3B30; }

.overall-box {
    background: linear-gradient(135deg, #0064FF 0%, #3D8BFF 100%);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    color: #fff;
    margin-bottom: 0.75rem;
    text-align: center;
}
.overall-score { font-size: 2.5rem; font-weight: 700; }
.overall-label { font-size: 0.88rem; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)


# ── Helper ───────────────────────────────────────────────────────────────────
def api(method: str, path: str, **kwargs):
    try:
        r = getattr(requests, method)(f"{API_BASE}{path}", timeout=60, **kwargs)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "API 서버 미연결"
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = e.response.text or str(e)
        return None, detail
    except Exception as e:
        return None, str(e)


def score_class(v: float):
    if v >= 0.7:
        return "c-green", "bg-green"
    if v >= 0.4:
        return "c-orange", "bg-orange"
    return "c-red", "bg-red"


def sim_class(v: float):
    if v >= 0.7:
        return "sim-high"
    if v >= 0.4:
        return "sim-mid"
    return "sim-low"


def check_api():
    d, e = api("get", "/health")
    return e is None

def check_indexed():
    d, e = api("get", "/embed/status")
    return bool(d and d.get("indexed"))


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-label">API 상태</div>', unsafe_allow_html=True)
    api_ok = check_api()
    if "indexed" not in st.session_state:
        st.session_state["indexed"] = check_indexed()
    dot = "api-on" if api_ok else "api-off"
    label = "연결됨" if api_ok else "미연결 — uvicorn 실행 필요"
    st.markdown(f'<span class="api-dot {dot}"></span><span style="font-size:0.85rem;color:#191F28;font-weight:500">{label}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">청킹 설정</div>', unsafe_allow_html=True)
    st.caption("문서를 몇 글자씩 자를지 설정합니다.")
    chunk_size    = st.slider("Chunk Size", 100, 1000, 300, 50)
    st.markdown('<span style="font-size:0.75rem;color:#B0B8C1">↑ 청크 하나의 최대 글자 수. 클수록 문맥이 풍부하지만 검색 정밀도 ↓</span>', unsafe_allow_html=True)
    chunk_overlap = st.slider("Overlap",      0,  200,  50, 10)
    st.markdown('<span style="font-size:0.75rem;color:#B0B8C1">↑ 청크 간 겹치는 글자 수. 크면 문맥 연결이 자연스러워짐</span>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label" style="margin-top:1.2rem">검색 설정</div>', unsafe_allow_html=True)
    st.caption("Step 5에서 몇 개의 청크를 가져올지 설정합니다.")
    top_k = st.slider("Top-K", 1, 8, 3)
    st.markdown('<span style="font-size:0.75rem;color:#B0B8C1">↑ 검색 결과 수. 많을수록 참고 자료 ↑, 프롬프트 길이 ↑</span>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label" style="margin-top:1.2rem">프롬프트</div>', unsafe_allow_html=True)
    styles_data, _ = api("get", "/prompt-styles")
    style_opts     = styles_data["styles"] if styles_data else ["기본", "엄격", "모르면모른다"]
    prompt_style   = st.selectbox("스타일", style_opts, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">사전 인덱싱</div>', unsafe_allow_html=True)
    st.caption("문서 로딩 → 청킹 → 임베딩 → DB 저장")
    if st.session_state.get("indexed"):
        st.markdown('<span style="font-size:0.8rem;color:#00C471;font-weight:600">● 인덱싱 완료</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="font-size:0.8rem;color:#FF3B30;font-weight:600">● DB 비어있음</span>', unsafe_allow_html=True)
    if st.button("인덱싱 실행"):
        with st.spinner("임베딩 중…"):
            d, e   = api("post", "/embed", json={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap})
            docs_d, _ = api("get", "/load")
            chk_d, _  = api("post", "/chunk", json={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap})
        if e:
            st.error(e)
        else:
            st.session_state["indexed"] = True
            st.session_state["index_result"] = {
                "embed": d,
                "docs":  docs_d,
                "chunks": chk_d,
            }
            st.rerun()
    if st.button("DB 초기화"):
        _, e = api("delete", "/embed")
        if e:
            st.error(e)
        else:
            st.session_state["indexed"] = False
            st.session_state.pop("result", None)
            st.session_state.pop("index_result", None)
            st.rerun()



# ── Main ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:4px">
  <img src="data:image/png;base64,{_logo_b64()}"
       style="width:40px;height:40px;object-fit:contain;flex-shrink:0">
  <div>
    <div style="display:flex;align-items:baseline;gap:8px">
      <span style="font-size:1.4rem;font-weight:800;color:#191F28;letter-spacing:-0.3px">RAG 파이프라인 이해하기</span>
      <span style="font-size:0.78rem;font-weight:600;color:#0064FF;
                   background:#E6F0FF;border-radius:99px;padding:2px 8px">NLP X AIE</span>
    </div>
    <div style="font-size:0.83rem;color:#6B7684;margin-top:1px">
      각 단계의 내부 동작을 확인하며 RAG를 파헤쳐봅시다!
    </div>
  </div>
</div>
<div style="height:1px;background:#E5E8EB;margin:14px 0 18px 0"></div>
""", unsafe_allow_html=True)

_indexed     = st.session_state.get("indexed", False)
_ir          = st.session_state.get("index_result", {})
_result_exists = "result" in st.session_state and _indexed

# 데이터 소스: 파이프라인 결과 우선, 없으면 인덱싱 결과 사용
_docs_src  = st.session_state.get("docs")  if _result_exists else _ir.get("docs")
_chunk_src = st.session_state.get("chunks") if _result_exists else _ir.get("chunks")
_em        = _ir.get("embed", {})

# ── Step 1: 문서 로딩 ────────────────────────────────────────────────────────
with st.expander("📂  Step 1 — 문서 로딩", expanded=_indexed):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    RAG의 첫 번째 단계입니다. <b>data/ 폴더에 있는 텍스트 파일들을 읽어오는 과정</b>이에요.<br>
    마치 AI에게 공부할 교과서를 건네주는 것과 같습니다.<br>
    <span style="color:#6B7684">→ 여기서 읽은 내용이 이후 모든 단계의 재료가 됩니다.</span>
  </div>
</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — loader.py"])
    with _t_res:
        if _docs_src:
            for doc in _docs_src["documents"]:
                st.markdown(f"""
<div class="step-row">
  <div class="step-badge done">✓</div>
  <div>
    <div class="step-title">{doc['filename']}</div>
    <div class="step-sub">{doc['char_count']:,}자 · {doc['line_count']}줄</div>
  </div>
</div>""", unsafe_allow_html=True)
                preview = doc["content"][:500] + ("…" if len(doc["content"]) > 500 else "")
                st.text_area("", preview, height=100, key=f"doc_{doc['filename']}", label_visibility="collapsed")
        else:
            st.caption("인덱싱 실행 후 문서 목록이 표시됩니다.")
    with _t_code:
        st.code('''from pathlib import Path

def load_documents(data_dir: str = "data") -> list[dict]:
    data_path = Path(data_dir)   # 📁 data/ 폴더 경로를 가리킵니다
    documents = []

    for file_path in sorted(data_path.glob("*.txt")):  # .txt 파일을 전부 찾아서
        content = file_path.read_text(encoding="utf-8") # 파일 내용을 텍스트로 읽고
        documents.append({
            "filename": file_path.name,  # 파일 이름
            "content":  content,         # 전체 텍스트 내용
            "char_count": len(content),  # 글자 수
        })

    return documents  # 문서 목록을 반환 → 다음 단계(청킹)로 전달''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • <code>Path</code>는 파이썬 내장 도구로, 파일 경로를 다루는 객체입니다<br>
  • <code>glob("*.txt")</code>는 폴더 안의 <code>.txt</code> 파일을 전부 찾아줍니다<br>
  • 함수가 <code>list[dict]</code>를 반환 → 다음 단계 함수의 입력으로 그대로 넘어갑니다<br>
  • <b>LangChain 미사용</b>: 이 단계는 순수 파이썬으로도 충분합니다
</div>""", unsafe_allow_html=True)

# ── Step 2: 청킹 ─────────────────────────────────────────────────────────────
with st.expander("✂️  Step 2 — 청킹", expanded=_indexed):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    긴 문서를 <b>작은 조각(청크)으로 잘게 나누는 과정</b>입니다.<br>
    왜 자를까요? AI는 한 번에 처리할 수 있는 글자 수 한계가 있고, 작게 나눠야 질문과 관련된 부분만 정확히 찾을 수 있거든요.<br>
    <span style="color:#6B7684">→ Chunk Size(크기)와 Overlap(겹침)을 사이드바에서 직접 조절해보세요!</span>
  </div>
</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — chunker.py"])
    with _t_res:
        if _chunk_src:
            c1, c2, c3 = st.columns(3)
            c1.metric("총 청크", f"{_chunk_src['total_chunks']}개")
            c2.metric("Chunk Size", f"{_chunk_src['chunk_size']}자")
            c3.metric("Overlap", f"{_chunk_src['chunk_overlap']}자")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            for c in _chunk_src["chunks"]:
                st.markdown(f"""
<div class="chunk-meta">#{c['chunk_id']} · {c['source']} · {c['char_count']}자</div>
<div class="chunk-pill">{c['content']}</div>""", unsafe_allow_html=True)
        else:
            st.caption("인덱싱 실행 후 청킹 결과가 표시됩니다.")
    with _t_code:
        st.code('''from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def chunk_documents(documents, chunk_size=300, chunk_overlap=50):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,       # 청크 최대 글자 수 (사이드바 슬라이더 값)
        chunk_overlap=chunk_overlap, # 앞 청크와 겹치는 글자 수
        separators=["\\n\\n", "\\n", ". ", " ", ""],  # 이 순서로 잘라봅니다
    )

    langchain_docs = [
        Document(page_content=doc["content"],
                 metadata={"source": doc["filename"]})
        for doc in documents
    ]

    split_docs = splitter.split_documents(langchain_docs)
    return split_docs  # → 다음 단계(임베딩)로 전달''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • <code>RecursiveCharacterTextSplitter</code>: LangChain이 제공하는 텍스트 분할 도구입니다<br>
  • <code>separators</code> 우선순위: 문단 → 줄바꿈 → 마침표 → 공백 순으로 자릅니다. 자연스러운 경계를 먼저 찾아요<br>
  • <code>chunk_overlap</code>: 앞 청크의 끝부분을 다음 청크 시작에 포함 → 문맥이 끊기지 않도록 도와줍니다<br>
  • <b>백엔드 관점</b>: 이 함수는 API <code>POST /chunk</code> 엔드포인트에서 호출됩니다
</div>""", unsafe_allow_html=True)

# ── Step 3+4: 임베딩 & 저장 ──────────────────────────────────────────────────
with st.expander("🔢  Step 3+4 — 임베딩 & 저장", expanded=_indexed):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    각 청크를 <b>숫자 배열(벡터)로 변환해 데이터베이스에 저장</b>합니다. 이 숫자들이 문장의 "의미"를 담고 있어요.<br>
    비슷한 의미의 문장은 벡터 공간에서 가까운 위치에 놓입니다. 덕분에 나중에 질문과 의미가 비슷한 청크를 빠르게 찾을 수 있어요.<br>
    <span style="color:#6B7684">→ 이 단계는 사이드바 <b>인덱싱 실행</b>으로 미리 수행합니다. 질문할 때마다 반복하지 않아도 돼요.</span>
  </div>
</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — embedder.py"])
    with _t_res:
        if _em:
            c1, c2 = st.columns(2)
            c1.metric("저장된 청크", f"{_em.get('total_chunks_stored', '–')}개")
            c2.metric("벡터 차원", f"{_em.get('vector_dimensions', '–')}")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("""
<div class="toss-card" style="margin-top:0">
  <div class="step-row">
    <div class="step-badge">i</div>
    <div>
      <div class="step-title">텍스트 → 숫자 벡터</div>
      <div class="step-sub">의미가 비슷한 문장은 벡터 공간에서 가까이 위치합니다</div>
    </div>
  </div>
  <div style="background:#F2F4F6;border-radius:10px;padding:10px 14px;font-size:0.82rem;color:#6B7684;font-family:monospace">
    "RAG란 무엇인가?"  →  [0.023, -0.142, 0.891, …]  <span class="tag tag-blue">1536차원</span><br>
    "검색 증강 생성"    →  [0.021, -0.138, 0.887, …]  <span class="tag tag-green">유사!</span><br>
    "오늘 점심 메뉴"   →  [-0.43,  0.812, -0.023, …]  <span class="tag tag-gray">거리 멀다</span>
  </div>
</div>""", unsafe_allow_html=True)
        if not _em:
            st.caption("사이드바 → **인덱싱 실행** 버튼으로 임베딩 & ChromaDB 저장을 수행합니다.")
    with _t_code:
        st.code('''from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def embed_and_store(chunks, chroma_path="./chroma_db"):

    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-small"  # 1536차원 벡터를 만들어줍니다
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,               # 앞 단계에서 만든 청크들
        embedding=embedding_model,      # 변환에 쓸 모델
        persist_directory=chroma_path,  # 저장 위치 (디스크에 영구 저장!)
    )
    # 이제 chroma_db/ 폴더에 벡터 DB가 생겼습니다 ✓''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • <code>OpenAIEmbeddings</code>: OpenAI API를 호출해 텍스트를 1536개 숫자 배열(벡터)로 바꿔줍니다<br>
  • <code>Chroma.from_documents()</code>: 변환 + 저장을 한 줄로 처리해주는 LangChain의 편의 메서드입니다<br>
  • <code>persist_directory</code>: 결과를 디스크에 저장하므로, 다음에 앱을 켜도 다시 인덱싱할 필요가 없어요<br>
  • <b>백엔드 관점</b>: <code>POST /embed</code> 요청 → 이 함수 실행 → <code>chroma_db/</code> 폴더 생성
</div>""", unsafe_allow_html=True)

# ── 질문 입력 (Step 3+4 아래) ────────────────────────────────────────────────
st.markdown("""
<div style="height:1px;background:#E5E8EB;margin:20px 0 16px 0"></div>
<div style="font-size:0.75rem;font-weight:700;color:#B0B8C1;letter-spacing:0.08em;
            text-transform:uppercase;margin-bottom:10px">Step 5~8 실행 — 질문 입력</div>
""", unsafe_allow_html=True)

if "prefill_query" in st.session_state:
    st.session_state["query_input"] = st.session_state.pop("prefill_query")
query = st.text_input("", placeholder="질문을 입력하세요  예) RAG란 무엇인가요?", key="query_input", label_visibility="collapsed")
run   = st.button("파이프라인 실행", type="primary")

if run and not query.strip():
    st.warning("질문을 입력하세요.")

if run and query.strip():
    if not api_ok:
        st.error("API 서버가 실행 중이지 않습니다.")
        st.stop()
    if not _indexed:
        st.markdown("""
<div style="background:#FFF8EC;border:1px solid #FFD580;border-radius:14px;padding:18px 20px;
            display:flex;align-items:flex-start;gap:14px;margin-top:8px">
  <span style="font-size:1.4rem;flex-shrink:0">⚠️</span>
  <div>
    <div style="font-size:0.92rem;font-weight:700;color:#191F28;margin-bottom:6px">인덱싱이 필요합니다</div>
    <div style="font-size:0.82rem;color:#6B7684;line-height:1.7">
      RAG는 질문에 답하기 전에 <b>문서를 미리 벡터로 변환해 DB에 저장</b>해야 합니다.<br>
      사이드바에서 <b>인덱싱 실행</b>을 클릭해 먼저 문서를 임베딩하세요.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        st.stop()

    _prog = st.empty()

    def _draw_steps(done: set, active: set = set()):
        _steps = [
            ("5",   "유사도 검색"),
            ("6",   "프롬프트 증강"),
            ("7",   "답변 생성"),
            ("8",   "평가"),
        ]
        rows = []
        for k, label in _steps:
            if k in done:
                b = "background:#00C471;color:#fff"; t = "color:#191F28"
                txt = "✓"
            elif k in active:
                b = "background:#0064FF;color:#fff"; t = "color:#0064FF;font-weight:600"
                txt = "…"
            else:
                b = "background:#F2F4F6;color:#B0B8C1"; t = "color:#B0B8C1"
                txt = k
            rows.append(
                f'<div style="display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid #F2F4F6">'
                f'<div style="width:28px;height:28px;border-radius:50%;{b};display:flex;align-items:center;'
                f'justify-content:center;font-size:0.72rem;font-weight:700;flex-shrink:0">{txt}</div>'
                f'<span style="font-size:0.88rem;font-weight:500;{t}">Step {k} — {label}</span>'
                f'</div>'
            )
        _prog.markdown(
            '<div style="background:#fff;border:1px solid #E5E8EB;border-radius:16px;padding:4px 20px;margin-top:12px">'
            + "".join(rows) + '</div>',
            unsafe_allow_html=True,
        )

    _draw_steps(set(), active={"5", "6", "7", "8"})
    _docs, _ = api("get", "/load")
    _chunks, _ = api("post", "/chunk", json={"chunk_size": chunk_size, "chunk_overlap": chunk_overlap})
    _data, err = api("post", "/pipeline", json={"query": query, "top_k": top_k, "prompt_style": prompt_style})

    if err:
        _prog.empty()
        st.error(f"오류: {err}")
        st.stop()

    _draw_steps({"5", "6", "7", "8"})

    st.session_state["result"]  = _data
    st.session_state["docs"]    = _docs
    st.session_state["chunks"]  = _chunks
    st.session_state["q"]       = query
    st.session_state["top_k"]   = top_k
    st.session_state["style"]   = prompt_style
    st.rerun()

if not _indexed:
    st.session_state.pop("result", None)

if "result" not in st.session_state:
    st.markdown('<div style="margin-top:16px;margin-bottom:10px"><div class="sidebar-label">추천 질문</div></div>', unsafe_allow_html=True)
    _questions = [
        ("🔍", "RAG의 장점은 무엇인가요?"),
        ("📐", "임베딩 차원은 몇 개인가요?"),
        ("🗄️", "Chroma와 Pinecone의 차이는?"),
        ("🤖", "프롬프트 템플릿은 어떻게 작동하나요?"),
    ]
    for _emoji, _q in _questions:
        if st.button(f"{_emoji}  {_q}", key=f"qbtn_{_q}", use_container_width=True):
            st.session_state["prefill_query"] = _q
            st.rerun()
    st.stop()

data         = st.session_state["result"]
docs_data    = st.session_state["docs"]
chunk_data   = st.session_state["chunks"]
q            = st.session_state["q"]
top_k        = st.session_state["top_k"]
prompt_style = st.session_state["style"]

# ── 파이프라인 완료 요약 바 (Step 5~8) ──────────────────────────────────────
_summary_steps = [("5", "검색"), ("6", "증강"), ("7", "생성"), ("8", "평가")]
_sep = '<span style="color:#B0B8C1;margin:0 2px;font-size:0.75rem">›</span>'
_chips = _sep.join(
    f'<span style="display:inline-flex;align-items:center;gap:5px">'
    f'<span style="width:18px;height:18px;border-radius:50%;background:#00C471;color:#fff;'
    f'font-size:0.62rem;font-weight:700;display:inline-flex;align-items:center;justify-content:center">✓</span>'
    f'<span style="font-size:0.78rem;font-weight:500;color:#191F28">{label}</span></span>'
    for _, label in _summary_steps
)
st.markdown(
    f'<div style="background:#F0FBF5;border:1px solid #B7EDD2;border-radius:12px;'
    f'padding:10px 16px;display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;margin-bottom:16px">'
    f'{_chips}</div>',
    unsafe_allow_html=True,
)

# ── Step 5: 검색 ─────────────────────────────────────────────────────────────
with st.expander("🔎  Step 5 — 유사도 검색", expanded=True):
    st.markdown(f"""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    질문을 벡터로 변환한 뒤, <b>DB에 저장된 청크들과 얼마나 의미가 비슷한지 점수를 매겨 상위 {top_k}개를 가져옵니다.</b><br>
    단순히 같은 단어를 찾는 게 아니라 <b>의미 기반 검색</b>이에요. "강아지"와 "반려견"도 유사하다고 판단할 수 있죠.<br>
    <span style="color:#6B7684">→ 유사도 점수가 높을수록(1에 가까울수록) 질문과 관련성이 높은 청크입니다.</span>
  </div>
</div>
<div class="chunk-meta">질문: <b>{q}</b> · Top-{top_k} 검색 결과</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — retriever.py"])
    with _t_res:
        st.markdown(f'<div class="chunk-meta">질문: <b>{q}</b> · Top-{top_k} 검색 결과</div>', unsafe_allow_html=True)
        for chunk in data["retrieved"]:
            s  = chunk["similarity_score"]
            sc = sim_class(s)
            st.markdown(f"""
<div class="toss-card" style="margin-bottom:8px">
  <div style="display:flex;align-items:center;margin-bottom:6px">
    <span class="step-badge" style="background:#E6F0FF;color:#0064FF;font-size:0.9rem">#{chunk['rank']}</span>
    <span style="margin-left:10px;font-size:0.85rem;font-weight:600;color:#191F28">{chunk['source']}</span>
    <span class="sim-badge {sc}">{s:.3f}</span>
  </div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.6">{chunk['content']}</div>
</div>""", unsafe_allow_html=True)
    with _t_code:
        st.code('''from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

def retrieve(query, top_k=3, chroma_path="./chroma_db"):

    vectorstore = Chroma(
        persist_directory=chroma_path,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    )

    results = vectorstore.similarity_search_with_relevance_scores(
        query,   # 사용자가 입력한 질문
        k=top_k  # 몇 개 가져올지 (사이드바 Top-K 슬라이더 값)
    )
    # results = [(Document, 유사도점수), ...]
    # 유사도는 0~1 사이, 1에 가까울수록 질문과 관련성 높음''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • <code>similarity_search_with_relevance_scores()</code>: 질문도 벡터로 바꾼 뒤, DB의 모든 청크 벡터와 거리를 계산합니다<br>
  • 거리 계산 방식은 <b>코사인 유사도</b>: 두 벡터가 같은 방향을 가리킬수록 점수가 높아요<br>
  • 키워드 없이 의미만 비슷해도 검색됩니다 (예: "개" 질문 → "반려동물" 청크 검색 가능)<br>
  • <b>백엔드 관점</b>: <code>POST /pipeline</code> 요청 시 내부에서 이 함수가 가장 먼저 호출됩니다
</div>""", unsafe_allow_html=True)

# ── Step 6: 프롬프트 증강 ────────────────────────────────────────────────────
with st.expander("📝  Step 6 — 프롬프트 증강", expanded=True):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    검색된 청크(참고 자료)와 질문을 합쳐 <b>AI에게 전달할 최종 지시문(프롬프트)을 만드는 단계</b>입니다.<br>
    "이 자료들을 참고해서 이 질문에 답해줘" 라고 AI에게 전달하는 거예요.<br>
    <span style="color:#6B7684">→ 프롬프트 스타일(기본/엄격/모르면모른다)을 바꾸면 AI의 답변 태도가 달라집니다!</span>
  </div>
</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — generator.py"])
    with _t_res:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
  <span style="font-size:0.82rem;color:#6B7684;font-weight:500">시스템 프롬프트</span>
  <span class="tag tag-blue">{prompt_style}</span>
</div>
<div style="background:#F2F8FF;border-radius:10px;padding:10px 14px;font-size:0.85rem;color:#191F28;margin-bottom:12px">
  {data['system_prompt']}
</div>""", unsafe_allow_html=True)
        st.text_area("최종 프롬프트 (LLM 전달 내용)", data["full_prompt"], height=260, label_visibility="visible")
    with _t_code:
        st.code('''def build_prompt(query, retrieved_chunks):
    context_parts = []
    for chunk in retrieved_chunks:
        context_parts.append(f"[출처: {chunk[\'source\']}]\\n{chunk[\'content\']}")

    context = "\\n\\n---\\n\\n".join(context_parts)  # 청크 사이에 구분선

    prompt = f"""다음 문서들을 참고하여 질문에 답변하세요.

=== 참고 문서 ===
{context}      ← Step 5에서 검색된 청크들이 여기 들어갑니다

=== 질문 ===
{query}        ← 사용자 질문

=== 답변 ===""  ← AI가 이 다음에 답변을 이어 씁니다
    return prompt''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • 이 단계에서 "증강(Augmented)"이 일어납니다 — 질문 단독이 아니라 참고자료를 <b>덧붙인(augment)</b> 프롬프트를 만들어요<br>
  • RAG의 R·A·G 중 <b>A(Augmented)</b>가 바로 이 단계입니다<br>
  • <code>f-string</code>: 파이썬에서 변수를 문자열 안에 넣는 방법 (<code>f"안녕 {이름}"</code>)<br>
  • 📊 결과 탭에서 실제로 어떻게 조립됐는지 직접 확인해보세요!
</div>""", unsafe_allow_html=True)

# ── Step 7: 답변 생성 ────────────────────────────────────────────────────────
with st.expander("💬  Step 7 — 답변 생성", expanded=True):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    만들어진 프롬프트를 <b>LLM(대형 언어 모델)에게 보내 실제 답변을 생성하는 단계</b>입니다.<br>
    AI는 우리가 준 참고 자료를 바탕으로만 답변하기 때문에, 엉뚱한 내용을 지어내는 "환각 현상"이 줄어들어요.<br>
    <span style="color:#6B7684">→ 입력/출력 토큰 수로 이 대화에 얼마나 많은 정보가 오갔는지 볼 수 있어요.</span>
  </div>
</div>""", unsafe_allow_html=True)
    _t_res, _t_code = st.tabs(["📊 결과", "🔍 코드 — generator.py"])
    with _t_res:
        col1, col2, col3 = st.columns(3)
        col1.metric("모델", data["model"])
        col2.metric("입력 토큰", data["token_usage"]["prompt_tokens"])
        col3.metric("출력 토큰", data["token_usage"]["completion_tokens"])
        st.markdown(f'<div class="answer-box">{data["answer"]}</div>', unsafe_allow_html=True)
    with _t_code:
        st.code('''from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

def generate(query, retrieved_chunks, prompt_style="기본"):

    llm = ChatOpenAI(
        model="gpt-4o-mini",  # 사용할 AI 모델
        temperature=0.1,      # 0에 가까울수록 일관된 답변 (창의성 ↓)
    )

    system_prompt = "당신은 친절한 AI 어시스턴트입니다..."  # 스타일에 따라 달라짐
    user_prompt = build_prompt(query, retrieved_chunks)  # Step 6 함수 호출

    messages = [
        SystemMessage(content=system_prompt),  # "너는 이런 역할이야"
        HumanMessage(content=user_prompt),     # "이 자료 보고 이 질문 답해줘"
    ]

    response = llm.invoke(messages)  # 실제 API 호출 → 답변 받기
    return response.content          # 텍스트 답변 반환''', language="python")
        st.markdown("""
<div style="background:#F8F9FA;border-radius:10px;padding:12px 16px;font-size:0.82rem;color:#191F28;line-height:1.8">
  <b>🔑 핵심 포인트</b><br>
  • <code>ChatOpenAI</code>: LangChain이 OpenAI API 호출을 대신 처리해주는 래퍼(wrapper)입니다<br>
  • <code>SystemMessage</code> vs <code>HumanMessage</code>: AI와 대화할 때 "역할 설정"과 "실제 질문"을 분리해 보냅니다<br>
  • <code>temperature=0.1</code>: 낮을수록 답변이 안정적, 높을수록 창의적(하지만 엉뚱해질 수 있음)<br>
  • <b>백엔드 관점</b>: <code>llm.invoke()</code> 한 줄이 실제 OpenAI 서버로 HTTP 요청을 보냅니다
</div>""", unsafe_allow_html=True)

# ── Step 8: 평가 ─────────────────────────────────────────────────────────────
with st.expander("📊  Step 8 — 평가", expanded=True):
    st.markdown("""
<div style="background:#F0F4FF;border-left:4px solid #0064FF;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:14px">
  <div style="font-size:0.8rem;font-weight:700;color:#0064FF;margin-bottom:4px">💡 이 단계는 무엇인가요?</div>
  <div style="font-size:0.85rem;color:#191F28;line-height:1.75">
    RAG 파이프라인이 얼마나 잘 작동했는지 <b>세 가지 기준으로 자동 평가</b>합니다.<br>
    &nbsp;&nbsp;• <b>컨텍스트 관련성</b>: 검색된 자료가 질문과 얼마나 관련 있나요?<br>
    &nbsp;&nbsp;• <b>충실도</b>: 답변이 검색된 자료에 근거하고 있나요? (지어내지 않았나요?)<br>
    &nbsp;&nbsp;• <b>답변 관련성</b>: 답변이 실제로 질문에 잘 답하고 있나요?<br>
    <span style="color:#6B7684">→ 점수가 낮은 항목을 보면 어디서 문제가 생겼는지 파악할 수 있어요.</span>
  </div>
</div>""", unsafe_allow_html=True)
    ev      = data["evaluation"]
    overall = ev.get("overall", 0.0)

    col_ov, col_detail = st.columns([1, 2])

    with col_ov:
        st.markdown(f"""
<div class="overall-box">
  <div class="overall-label">종합 점수</div>
  <div class="overall-score">{int(round(overall * 100))}<span style="font-size:1.2rem;opacity:0.7">점</span></div>
</div>""", unsafe_allow_html=True)

    with col_detail:
        items = [
            ("컨텍스트 관련성", "context_relevance", "context_relevance_reason"),
            ("충실도",          "faithfulness",       "faithfulness_reason"),
            ("답변 관련성",     "answer_relevance",   "answer_relevance_reason"),
        ]
        cards_html = ""
        for label, key, reason_key in items:
            v      = ev.get(key, 0.0)
            pct    = int(min(v, 1.0) * 100)
            tc, bc = score_class(v)
            reason = ev.get(reason_key, "")
            border_color = "#00C471" if tc == "c-green" else "#FF9500" if tc == "c-orange" else "#FF3B30"
            cards_html += f"""
<details style="margin-bottom:8px">
  <summary style="
    list-style:none;cursor:pointer;
    background:#fff;border-radius:14px;
    box-shadow:0 2px 10px rgba(0,0,0,0.06);
    padding:14px 16px;
    display:flex;align-items:center;gap:12px;
    user-select:none;
  ">
    <span style="flex:1;font-size:0.9rem;font-weight:600;color:#191F28">{label}</span>
    <div style="width:90px;background:#E5E8EB;border-radius:99px;height:6px;margin-right:12px">
      <div style="width:{pct}%;height:6px;border-radius:99px;background:{border_color}"></div>
    </div>
    <span style="font-size:1rem;font-weight:700;color:{border_color};width:32px;text-align:right">{int(round(v * 100))}</span>
    <span style="font-size:0.75rem;color:#B0B8C1;margin-left:8px">이유 ›</span>
  </summary>
  <div style="
    background:#F8F9FA;
    border-left:3px solid {border_color};
    border-radius:0 0 12px 12px;
    padding:12px 16px;
    font-size:0.85rem;color:#191F28;line-height:1.65;
    margin-top:-4px;
  ">{reason}</div>
</details>"""
        st.markdown(cards_html, unsafe_allow_html=True)

# ── 실습 가이드 ───────────────────────────────────────────────────────────────
with st.expander("📚  실습 가이드 — 시나리오별 따라하기"):
    st.markdown("""
<div style="font-size:0.85rem;color:#6B7684;margin-bottom:16px;line-height:1.7">
  아래 시나리오를 순서대로 따라하면 RAG 파이프라인의 핵심을 직접 체감할 수 있어요.<br>
  각 시나리오마다 <b>무엇을 보고, 무엇을 느껴야 하는지</b>를 꼭 확인하세요!
</div>

<div style="display:flex;flex-direction:column;gap:12px">

  <div class="toss-card" style="margin:0;padding:16px 18px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="step-badge" style="background:#E6F0FF;color:#0064FF;flex-shrink:0;width:28px;height:28px;font-size:0.85rem">1</div>
      <div style="font-size:0.95rem;font-weight:700;color:#191F28">전체 흐름 첫 체험</div>
    </div>
    <div style="font-size:0.83rem;color:#191F28;line-height:1.8;margin-left:38px">
      ① 사이드바에서 <b>인덱싱 실행</b> 클릭 (Step 1~3+4가 완료됩니다)<br>
      ② 질문 입력창에 <b>"RAG의 장점은 무엇인가요?"</b> 입력<br>
      ③ <b>파이프라인 실행</b> 클릭<br>
      ④ Step 5~8이 순서대로 채워지는 것을 확인하세요<br>
      <span style="color:#0064FF;font-weight:600">✔ 핵심 관찰: Step 5에서 어떤 문서 조각이 검색됐나요? 유사도 점수는 얼마인가요?</span>
    </div>
  </div>

  <div class="toss-card" style="margin:0;padding:16px 18px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="step-badge" style="background:#E6F0FF;color:#0064FF;flex-shrink:0;width:28px;height:28px;font-size:0.85rem">2</div>
      <div style="font-size:0.95rem;font-weight:700;color:#191F28">질문을 바꾸면 검색 결과도 바뀐다</div>
    </div>
    <div style="font-size:0.83rem;color:#191F28;line-height:1.8;margin-left:38px">
      ① 이번엔 <b>"임베딩이란 무엇인가요?"</b>로 질문을 바꿔보세요<br>
      ② 다시 파이프라인 실행<br>
      ③ Step 5의 검색 결과와 유사도 점수가 달라졌나요?<br>
      <span style="color:#0064FF;font-weight:600">✔ 핵심 관찰: 질문이 달라지면 다른 청크가 검색됩니다. 검색은 "키워드"가 아닌 "의미" 기반이에요!</span>
    </div>
  </div>

  <div class="toss-card" style="margin:0;padding:16px 18px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="step-badge" style="background:#E6F0FF;color:#0064FF;flex-shrink:0;width:28px;height:28px;font-size:0.85rem">3</div>
      <div style="font-size:0.95rem;font-weight:700;color:#191F28">Chunk Size를 바꾸면 어떻게 될까?</div>
    </div>
    <div style="font-size:0.83rem;color:#191F28;line-height:1.8;margin-left:38px">
      ① 사이드바에서 <b>Chunk Size를 100</b>으로 줄이기<br>
      ② <b>인덱싱 실행</b> → 청크 수가 늘어난 것을 Step 2에서 확인<br>
      ③ 같은 질문으로 파이프라인 실행<br>
      ④ 이번엔 <b>Chunk Size를 800</b>으로 키우고 반복<br>
      <span style="color:#0064FF;font-weight:600">✔ 핵심 관찰: 청크가 작으면 검색은 정밀하지만 문맥이 끊길 수 있고, 크면 문맥은 풍부하지만 노이즈가 생길 수 있어요.</span>
    </div>
  </div>

  <div class="toss-card" style="margin:0;padding:16px 18px">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="step-badge" style="background:#E6F0FF;color:#0064FF;flex-shrink:0;width:28px;height:28px;font-size:0.85rem">4</div>
      <div style="font-size:0.95rem;font-weight:700;color:#191F28">프롬프트 스타일로 AI 태도 바꾸기</div>
    </div>
    <div style="font-size:0.83rem;color:#191F28;line-height:1.8;margin-left:38px">
      ① 사이드바 프롬프트 스타일을 <b>"기본"</b>으로 설정 → 파이프라인 실행<br>
      ② <b>"엄격"</b>으로 바꾼 뒤 같은 질문 실행 → Step 7 답변 비교<br>
      ③ <b>"모르면모른다"</b>로 바꾼 뒤 <b>문서에 없는 질문</b>(예: "오늘 날씨는?") 입력<br>
      <span style="color:#0064FF;font-weight:600">✔ 핵심 관찰: 같은 자료라도 프롬프트에 따라 AI가 완전히 다르게 답합니다. Step 6의 시스템 프롬프트도 확인해보세요!</span>
    </div>
  </div>

  <div class="toss-card" style="margin:0;padding:16px 18px;border:1px solid #FFD0D0;background:#FFF8F8">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
      <div class="step-badge" style="background:#FFEDED;color:#FF3B30;flex-shrink:0;width:28px;height:28px;font-size:0.85rem">5</div>
      <div style="font-size:0.95rem;font-weight:700;color:#191F28">RAG의 한계 — 엉뚱한 질문을 넣으면?</div>
    </div>
    <div style="font-size:0.83rem;color:#191F28;line-height:1.8;margin-left:38px">
      ① 질문 입력창에 <b>"오늘 날씨가 어때요?"</b> 입력<br>
      ② 파이프라인 실행<br>
      ③ Step 5의 유사도 점수가 매우 낮은 것을 확인<br>
      ④ Step 8 평가 점수도 낮게 나오는 것을 확인<br>
      <span style="color:#FF3B30;font-weight:600">✔ 핵심 관찰: 문서에 없는 내용을 질문하면 검색도 실패하고, 답변 품질도 떨어집니다. RAG는 넣어준 문서 범위 안에서만 잘 작동해요!</span>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)
