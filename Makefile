test:
	poetry run python -m pytest --mypy

format:
	poetry run python -m black .