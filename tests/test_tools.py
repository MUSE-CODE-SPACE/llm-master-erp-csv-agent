"""Offline tests — restricted tools on the sample CSV. / 제한 도구 오프라인 테스트."""
from erp.tools import aggregate, filter_table, list_tables


def test_list():
    assert "revenue" in list_tables()["columns"]


def test_aggregate_guard():
    # only whitelisted ops via Literal; bad column returns error / 잘못된 컬럼은 에러
    assert "error" in aggregate("nope", "sum")


def test_filter_guard():
    assert "error" in filter_table("revenue", "LIKE", "1")  # op not whitelisted
