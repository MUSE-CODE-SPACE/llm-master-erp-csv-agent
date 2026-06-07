"""Natural-language sales queries. / 자연어 매출 질의."""
from erp.agent import ask


def _show(kind, p):
    if kind == "tool_call":
        print(f"  🔧 {p['name']}({p['args']})")
    elif kind == "tool_result":
        print(f"  📥 {str(p['result'])[:90]}")


def main() -> None:
    print("ERP CSV agent — ask about sales. / 매출을 물어보세요.")
    while True:
        try:
            q = input("\nQ> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye"); break
        if q:
            print(ask(q, on_event=_show))


if __name__ == "__main__":
    main()
