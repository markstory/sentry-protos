# Makefile assumes that direnv is active, or that pip/python on PATH
# is what you want to use.

.PHONY: update-venv
update-venv:
	pip install -r requirements.txt

# Python client targets
.PHONY: build-py
build-py:
	pip install -r requirements.txt
	python py/generate.py
	cat py/sentry_protos/__init__.py

.PHONY: package-py
package-py: build-py
	cd py && python -m build

.PHONY: clean-py
clean-py:
	rm -rf ./py/dist
	rm -rf ./py/sentry_protos
	rm -rf ./py/sentry_protos.egg-info

# Rust client targets
.PHONY: build-rust
build-rust:
	cargo run -p rustgenerator

.PHONY: clean-rust
clean-rust:
	cd rust && cargo clean

.PHONY: build
build: build-py build-rust
