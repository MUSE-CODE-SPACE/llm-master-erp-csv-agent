.PHONY: install data run test
install:; pip install -r requirements.txt
data:; python scripts/gen_data.py
run:; python -m erp.cli
test:; pytest -q
