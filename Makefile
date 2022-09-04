generate:
	python generate.py

deps:
	pip install -r requirements.txt
	mkdir -p static

env:
	python3 -m virtualenv env

clean:
	rm -rf ./static/*

serve:
	python serve.py

.PHONY: deps generate clean serve
