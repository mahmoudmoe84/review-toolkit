# Both targets are read-only. CI runs both on every push.

.PHONY: check security

check:
	ruff check .
	pytest -q

security:
	bandit -c pyproject.toml -r src/ tests/
	pip-audit -r requirements.txt --no-deps --disable-pip
