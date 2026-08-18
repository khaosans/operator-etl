.PHONY: install sync test e2e demo share docker-build docker-run clean help verify walkthrough

help:
	@echo "Operator ETL — common targets"
	@echo "  make verify    — bootstrap uv + full proof gate (first-time setup)"
	@echo "  make install   — uv sync --extra dev"
	@echo "  make test      — pytest"
	@echo "  make e2e       — full proof gate (OKF + tests + FOIA demo)"
	@echo "  make demo      — FOIA MVP demo only"
	@echo "  make walkthrough — demo + warehouse inspection"
	@echo "  make share     — regenerate share PDF pack (run e2e first)"
	@echo "  make docker-build — build Cloud Run image"
	@echo "  make okf       — validate OKF bundle"

verify:
	./scripts/verify.sh

walkthrough:
	./scripts/walkthrough.sh

install sync:
	uv sync --extra dev

test:
	uv run pytest -q

e2e:
	./harness/e2e.sh

demo:
	./scripts/demo_mvp.sh

share: e2e
	./scripts/share_pack.sh

okf:
	python3 scripts/okf_validate.py okf --strict

docker-build:
	docker build -t operator-etl:local .

docker-run:
	docker run --rm -p 8080:8080 operator-etl:local

clean:
	rm -rf .tmp/ .pytest_cache/ .ruff_cache/ src/*.egg-info/ dist/ build/
