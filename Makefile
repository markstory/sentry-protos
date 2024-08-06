# Python client targets
py:
	mkdir py

.PHONY: build-py
build-py: py
	.venv/bin/pip install .

# Rust client targets
.PHONY: build-rust
build-rust:
	cd rust && cargo build

.PHONY: build
build: build-py build-rust

.PHONY: update-venv
update-venv:
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e src
