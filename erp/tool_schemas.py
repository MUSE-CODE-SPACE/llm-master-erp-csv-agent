"""OpenAI-format tool schemas (hand-written, explicit). / 도구 스키마(명시)."""
SCHEMAS = [
    {"type": "function", "function": {"name": "list_tables",
     "description": "List the sales table and its columns. / 테이블·컬럼 목록.",
     "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "filter_table",
     "description": "Filter rows by one condition. / 한 조건으로 행 필터.",
     "parameters": {"type": "object", "properties": {
         "column": {"type": "string"}, "op": {"type": "string", "enum": [">", "<", ">=", "<=", "==", "!="]},
         "value": {"type": "string"}}, "required": ["column", "op", "value"]}}},
    {"type": "function", "function": {"name": "aggregate",
     "description": "Aggregate a numeric column, optionally grouped. / 집계(선택 그룹별).",
     "parameters": {"type": "object", "properties": {
         "column": {"type": "string"},
         "operation": {"type": "string", "enum": ["sum", "mean", "count", "min", "max"]},
         "group_by": {"type": "string"}}, "required": ["column", "operation"]}}},
]
