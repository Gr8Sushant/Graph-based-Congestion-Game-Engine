.PHONY: install test lint run-app build-graph clean

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	PYTHONPATH=. pytest tests/ -v

lint:
	ruff check .
	ruff format --check .

run-app:
	streamlit run src/app/streamlit_app.py

build-graph-brest:
	python scripts/build_graph.py --source osm --place "Brest, France"

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
