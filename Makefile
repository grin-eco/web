generate:
	python build/generate.py

deps:
	pip install -r build/requirements.txt
	mkdir -p static

env:
	python3 -m virtualenv env

clean:
	rm -rf ./static/*

theme:
	cp -r template/theme/css static
	cp -r template/theme/js static
	cp -r template/theme/plugins static
	cp -r assets static

serve:
	python build/serve.py

.PHONY: deps generate clean serve theme
