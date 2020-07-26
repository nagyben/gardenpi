test:
	poetry run python -m pytest --mypy

format:
	poetry run python -m black .

check:
	poetry run python -m prospector