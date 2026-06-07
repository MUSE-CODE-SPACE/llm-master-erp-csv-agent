"""RESTRICTED pandas tools — NOT arbitrary code. Whitelisted ops only.
제한된 pandas 도구 — 임의 코드 X. 화이트리스트 연산만."""
from typing import Literal

import pandas as pd

from erp.settings import settings

_df = None
_OPS = {">", "<", ">=", "<=", "==", "!="}


def _data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(settings.csv_path)
    return _df


def list_tables() -> dict:
    """List the table and its columns. / 테이블·컬럼 목록."""
    df = _data()
    return {"table": "sales", "columns": list(df.columns), "rows": len(df)}


def filter_table(column: str, op: str, value: str) -> dict:
    """Filter rows by a single condition (op in > < >= <= == !=). / 한 조건으로 필터."""
    df = _data()
    if column not in df.columns:
        return {"error": f"no column: {column}"}
    if op not in _OPS:
        return {"error": f"unsupported op: {op}"}
    try:
        v: object = float(value)
    except ValueError:
        v = value
    mask = getattr(df[column], {">": "gt", "<": "lt", ">=": "ge", "<=": "le", "==": "eq", "!=": "ne"}[op])(v)
    sub = df[mask]
    return {"matched": int(len(sub)), "sample": sub.head(5).to_dict(orient="records")}


def aggregate(
    column: str,
    operation: Literal["sum", "mean", "count", "min", "max"],
    group_by: str = "",
) -> dict:
    """Aggregate a numeric column, optionally grouped. / 집계(선택: 그룹별). 정해진 연산만."""
    df = _data()
    if column not in df.columns:
        return {"error": f"no column: {column}"}
    if group_by and group_by in df.columns:
        res = getattr(df.groupby(group_by)[column], operation)()
        return {"operation": operation, "by": group_by, "result": res.round(2).to_dict()}
    res = getattr(df[column], operation)()
    return {"operation": operation, "result": round(float(res), 2)}


TOOLS = [list_tables, filter_table, aggregate]
REGISTRY = {t.__name__: t for t in TOOLS}
