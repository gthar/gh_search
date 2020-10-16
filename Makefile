install:
	python setup.py install

init:
	pip install -r requirements.txt

test:
	python -m unittest discover

flake8:
	flake8

.PHONY: init test install
