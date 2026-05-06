import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

PROMPT_STYLES = {
    "기본": "당신은 친절한 AI 어시스턴트입니다. 주어진 문서를 바탕으로 질문에 답변하세요.",
    "엄격": "당신은 정확한 AI 어시스턴트입니다. 반드시 아래 문서에 있는 내용만 사용하여 답변하세요. 문서에 없는 내용은 '문서에서 찾을 수 없습니다'라고 말하세요.",
    "모르면모른다": "당신은 솔직한 AI 어시스턴트입니다. 주어진 문서를 바탕으로 답변하되, 확실하지 않거나 문서에 없는 내용은 반드시 '모르겠습니다'라고 답하세요.",
}


def build_prompt(query: str, retrieved_chunks: list[dict], prompt_style: str = "기본") -> str:
    context_parts = []
    for chunk in retrieved_chunks:
        context_parts.append(f"[출처: {chunk['source']}]\n{chunk['content']}")
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""다음 문서들을 참고하여 질문에 답변하세요.

=== 참고 문서 ===
{context}

=== 질문 ===
{query}

=== 답변 ==="""
    return prompt


def generate(
    query: str,
    retrieved_chunks: list[dict],
    prompt_style: str = "기본",
) -> dict:
    """Generate answer from retrieved chunks using LLM."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    system_prompt = PROMPT_STYLES.get(prompt_style, PROMPT_STYLES["기본"])
    user_prompt = build_prompt(query, retrieved_chunks, prompt_style)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)

    return {
        "query": query,
        "prompt_style": prompt_style,
        "system_prompt": system_prompt,
        "full_prompt": user_prompt,
        "answer": response.content,
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "prompt_tokens": response.usage_metadata.get("input_tokens", 0) if response.usage_metadata else 0,
        "completion_tokens": response.usage_metadata.get("output_tokens", 0) if response.usage_metadata else 0,
    }
