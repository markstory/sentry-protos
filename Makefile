# Makefile assumes that direnv is active, or that pip/python on PATH
# is what you want to use.

# Python client targets
.PHONY: build-py
build-py: update-venv
	pip install .

# Rust client targets
.PHONY: build-rust
build-rust:
	cd rust && cargo build

.PHONY: build
build: build-py build-rust

.PHONY: update-venv
update-venv:
	pip install -r requirements.txt
	pip install -e src
