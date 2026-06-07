"""Tool-use loop over RESTRICTED tools. Multi-vendor. / 제한 도구 위 tool_use 루프."""
import json

from erp.audit import log_query
from erp.settings import settings
from erp.tools import REGISTRY
from erp.tool_schemas import SCHEMAS

SYSTEM = (
    "You answer questions about a sales CSV using ONLY the provided tools "
    "(no raw code). Always fetch data with tools before answering in Korean. "
    "도구로만 데이터를 가져와 한국어로 답하라. 임의 코드 실행 없음."
)
_client = None


def _llm():
    global _client
    if _client is not None:
        return _client
    from openai import OpenAI

    if settings.provider == "ollama":
        _client = OpenAI(base_url=settings.ollama_base_url, api_key="ollama")
    else:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def ask(question: str, user_id: str = "demo", on_event=None) -> str:
    client = _llm()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    calls_log = []
    for _ in range(settings.max_steps):
        resp = client.chat.completions.create(
            model=settings.llm_model, messages=messages, tools=SCHEMAS, tool_choice="auto")
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            log_query(user_id, question, calls_log, msg.content or "")
            return msg.content or ""
        for tc in msg.tool_calls:
            name, args = tc.function.name, json.loads(tc.function.arguments or "{}")
            calls_log.append({"name": name, "args": args})
            if on_event:
                on_event("tool_call", {"name": name, "args": args})
            out = REGISTRY[name](**args) if name in REGISTRY else {"error": "unknown"}
            if on_event:
                on_event("tool_result", {"result": out})
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(out, ensure_ascii=False)})
    return "Reached max steps. / 최대 단계 도달."
