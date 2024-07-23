# Python client targets
py:
	mkdir py

.PHONY: build-py
build-py: py
	.venv/bin/pip install .

# Rust client targets
.PHONY: build-rs
build-rs:
	


.PHONY: build
build: build-py build-rs

.PHONY: update-venv
update-venv:
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e src
