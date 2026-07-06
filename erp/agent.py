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
    if settings.provider == "anthropic":
        from anthropic import Anthropic

        _client = ("anthropic", Anthropic(api_key=settings.anthropic_api_key))
    else:
        # openai or ollama (both speak the OpenAI Chat API) / openai·ollama는 같은 API
        from openai import OpenAI

        if settings.provider == "ollama":
            _client = ("openai", OpenAI(base_url=settings.ollama_base_url, api_key="ollama"))
        else:
            _client = ("openai", OpenAI(api_key=settings.openai_api_key))
    return _client


def to_anthropic_tools(schemas: list) -> list:
    """Convert OpenAI function schemas to Anthropic tool format.
    OpenAI: {"type": "function", "function": {name, description, parameters}}
    Anthropic: {name, description, input_schema}
    OpenAI 도구 스키마를 Anthropic 형식으로 변환."""
    return [
        {
            "name": s["function"]["name"],
            "description": s["function"]["description"],
            "input_schema": s["function"]["parameters"],
        }
        for s in schemas
    ]


def _ask_anthropic(client, question: str, user_id: str, on_event=None) -> str:
    """Tool-use loop, Anthropic Messages API flavor. / Anthropic 도구 호출 루프."""
    tools = to_anthropic_tools(SCHEMAS)
    messages = [{"role": "user", "content": question}]
    calls_log = []
    for _ in range(settings.max_steps):
        resp = client.messages.create(
            model=settings.llm_model, max_tokens=1024, system=SYSTEM,
            messages=messages, tools=tools,
        )
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text")
            log_query(user_id, question, calls_log, answer)
            return answer
        # Echo the assistant turn, then attach one tool_result per tool_use.
        # 어시스턴트 턴을 되돌려주고 tool_use마다 tool_result를 첨부.
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            name, args = block.name, dict(block.input or {})
            calls_log.append({"name": name, "args": args})
            if on_event:
                on_event("tool_call", {"name": name, "args": args})
            out = REGISTRY[name](**args) if name in REGISTRY else {"error": "unknown"}
            if on_event:
                on_event("tool_result", {"result": out})
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(out, ensure_ascii=False)})
        messages.append({"role": "user", "content": results})
    return "Reached max steps. / 최대 단계 도달."


def ask(question: str, user_id: str = "demo", on_event=None) -> str:
    kind, client = _llm()
    if kind == "anthropic":
        return _ask_anthropic(client, question, user_id, on_event)
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
