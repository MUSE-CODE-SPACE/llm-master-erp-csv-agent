<!-- 🌏 English + 한국어 (English first) -->
# ERP CSV Agent / ERP CSV 에이전트

> Ask a sales CSV in **natural language**. The agent uses **restricted, whitelisted pandas tools** (no arbitrary code), runs a tool-use loop, and writes an **audit log**. A miniature of where enterprise ERP meets LLMs. Runs on OpenAI / Anthropic / local SLM.
> 매출 CSV를 **자연어**로 질의. **제한된(화이트리스트) pandas 도구**만 쓰고(임의 코드 X), tool_use 루프로 답하며 **감사 로그**를 남긴다. ERP × LLM의 축소판. 멀티 벤더.

> 📱 Hands-on code for the **[LLM Master](https://apps.apple.com/app/id6769785318)** course — "실전 프로젝트 4: ERP CSV Agent".

**Safety first / 안전 원칙**: the model never runs raw code — only `list_tables`, `filter_table` (op whitelist), `aggregate` (operation `Literal[sum,mean,count,min,max]`). 모델은 임의 코드를 못 돌리고, 정해진 도구만 쓴다.

## Run / 실행
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/gen_data.py     # sample data/sales.csv / 샘플 생성
cp .env.example .env           # OPENAI_API_KEY
python -m erp.cli
# Q> 어느 제품이 제일 잘 팔렸어?
```
Real run / 실제 실행:
```
🔧 aggregate({column:'revenue', operation:'sum', group_by:'product'})
A> 볼트 D: 1,875,000원 ... 제일 잘 팔린 제품은 볼트 D 입니다.
```

| File | What / 하는 일 |
|---|---|
| `erp/tools.py` | restricted pandas tools (whitelist) |
| `erp/agent.py` | tool-use loop, multi-vendor |
| `erp/audit.py` | SQLite audit log (user·question·tools·answer) |
| `erp/cli.py` | natural-language queries |
| `scripts/gen_data.py` | deterministic sample CSV |

`PROVIDER=openai|anthropic|ollama`. License MIT (educational / 교육용).
