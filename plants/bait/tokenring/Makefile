.PHONY: check security

check:
	ruff check .

security:
	bandit -r src/
	pip-audit -r requirements.txt --no-deps --disable-pip
