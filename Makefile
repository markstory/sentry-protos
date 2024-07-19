.PHONY: build
build:
	mkdir py || true
	.venv/bin/pip install .

.PHONY: update-venv
update-venv:
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e src
