.PHONY: install run run-gui clean

install:
	pip install -r requirements.txt

run:
	python -m src.core

run-gui:
	python -m src.gui

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
