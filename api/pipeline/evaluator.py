import os
import json
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


EVAL_PROMPT = """당신은 극도로 엄격한 RAG 시스템 심사위원입니다. 점수는 후하게 주지 마세요. 조금이라도 문제가 있으면 감점합니다.

=== 채점 기준 (0.0 ~ 1.0) ===

[1] context_relevance — 검색된 문서가 질문에 얼마나 직접적으로 관련 있는가?
  - 1.0: 모든 청크가 질문의 핵심 키워드·개념을 정확히 다룸
  - 0.7: 대부분 관련 있으나 일부 청크가 주변 정보에 그침
  - 0.4: 질문과 간접적으로만 연관되거나 관련 청크가 절반 이하
  - 0.1: 질문과 주제가 다르거나 엉뚱한 문서가 검색됨
  - 0.0: 완전히 무관한 문서만 검색됨

[2] faithfulness — 답변이 오직 검색된 문서에 근거하는가? 문서에 없는 내용을 생성했는가?
  - 1.0: 답변의 모든 문장이 제공된 문서에서 직접 근거를 찾을 수 있음
  - 0.7: 대부분 문서 기반이나 한두 문장이 문서 밖 추론을 포함
  - 0.4: 문서에 없는 내용이 30% 이상 포함되어 있음
  - 0.1: 대부분 문서와 무관하게 지어낸 내용 (hallucination)
  - 0.0: 문서를 전혀 참고하지 않은 답변

[3] answer_relevance — 최종 답변이 질문을 정확하고 충분하게 해결하는가?
  - 1.0: 질문의 모든 측면에 구체적이고 완전하게 답변
  - 0.7: 핵심은 맞지만 일부 측면이 빠지거나 너무 짧음
  - 0.4: 질문에 부분적으로만 답하거나 핵심을 비껴감
  - 0.1: 질문과 거의 관련 없는 답변
  - 0.0: 질문을 완전히 무시한 답변

=== 감점 필수 상황 ===
- 검색된 문서에 "모른다", "문서에 없다"고 했음에도 답변을 지어낸 경우 → faithfulness 0.0
- 질문이 문서 범위 밖임에도 자신 있게 답변한 경우 → faithfulness -0.3
- 답변이 50자 미만으로 지나치게 짧은 경우 → answer_relevance -0.2
- 동일 청크가 여러 번 검색된 경우(중복) → context_relevance -0.2

=== 입력 ===
질문: {query}

검색된 문서:
{context}

생성된 답변:
{answer}

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 절대 금지):
{{
  "context_relevance": 0.0,
  "faithfulness": 0.0,
  "answer_relevance": 0.0,
  "context_relevance_reason": "구체적인 감점·가점 이유 한 줄",
  "faithfulness_reason": "구체적인 감점·가점 이유 한 줄",
  "answer_relevance_reason": "구체적인 감점·가점 이유 한 줄"
}}"""


def evaluate(
    query: str,
    retrieved_chunks: list[dict],
    answer: str,
) -> dict:
    """Evaluate RAG output using LLM-as-judge."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    context = "\n\n".join(
        f"[{c['rank']}] (유사도: {c['similarity_score']}) {c['content']}"
        for c in retrieved_chunks
    )

    prompt = EVAL_PROMPT.format(query=query, context=context, answer=answer)

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scores = json.loads(raw.strip())
    except Exception:
        scores = {
            "context_relevance": 0.0,
            "faithfulness": 0.0,
            "answer_relevance": 0.0,
            "context_relevance_reason": "파싱 오류",
            "faithfulness_reason": "파싱 오류",
            "answer_relevance_reason": "파싱 오류",
        }

    scores["overall"] = round(
        (scores["context_relevance"] + scores["faithfulness"] + scores["answer_relevance"]) / 3, 4
    )

    return scores
