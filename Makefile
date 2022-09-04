generate:
	python generate.py

deps:
	pip install -r requirements.txt
	mkdir -p static

env:
	python3 -m virtualenv env

clean:
	rm -rf ./static/*

.PHONY: deps generate clean
