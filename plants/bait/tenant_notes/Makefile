# The project's gates. `make check` is lint and tests; `make security` is the
# security gate. Both are read-only.

.PHONY: check security

check:
	ruff check .
	pytest -q

security:
	bandit -r src/
	pip-audit -r requirements.txt --no-deps --disable-pip
