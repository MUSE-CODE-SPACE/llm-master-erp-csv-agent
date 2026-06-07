"""Generate a deterministic sample sales.csv. / 결정적 샘플 매출 CSV 생성."""
import csv
from pathlib import Path

PRODUCTS = ["위젯 A", "위젯 B", "기어 C", "볼트 D", "패널 E"]
REGIONS = ["서울", "부산", "대구"]


def generate(path: str = "data/sales.csv", n: int = 300) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(n):
        p = PRODUCTS[i % len(PRODUCTS)]
        qty = 1 + (i * 7 + 3) % 20            # deterministic / 결정적
        unit = 1000 + (PRODUCTS.index(p) * 500)
        rows.append({
            "order_id": 1000 + i,
            "date": f"2026-{1 + i % 6:02d}-{1 + i % 27:02d}",
            "product": p,
            "region": REGIONS[i % len(REGIONS)],
            "quantity": qty,
            "revenue": qty * unit,
        })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} rows -> {path}")


if __name__ == "__main__":
    generate()
