# Both targets are read-only. CI runs both on every push — .github/workflows/ci.yml.
# bandit scans tests/ as well as src/: a key literal in a fixture is what §S1
# forbids, so a gate blind to tests/ would be blind to the rule it enforces.

.PHONY: check security

check:
	ruff check .
	pytest -q

security:
	bandit -c pyproject.toml -r src/ tests/
	pip-audit -r requirements.txt --no-deps --disable-pip
