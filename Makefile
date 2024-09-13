# Makefile assumes that direnv is active, or that pip/python on PATH
# is what you want to use.

# unstable protos are only included in local development and not part of release packages
SENTRY_PROTOS_BUILD_UNSTABLE := 1

.PHONY: update-venv
update-venv:
	pip install -r requirements.txt

# Python client targets
.PHONY: build-py
build-py:
	pip install -r requirements.txt
	SENTRY_PROTOS_BUILD_UNSTABLE=$(SENTRY_PROTOS_BUILD_UNSTABLE) python py/generate.py

.PHONY: package-py
package-py:
	make build-py SENTRY_PROTO_BUILD_UNSTABLE=0
	cd py && python -m build

.PHONY: clean-py
clean-py:
	rm -rf ./py/dist
	rm -rf ./py/sentry_protos
	rm -rf ./py/sentry_protos.egg-info

# Rust client targets
.PHONY: build-rust
build-rust:
	SENTRY_PROTOS_BUILD_UNSTABLE=$(SENTRY_PROTOS_BUILD_UNSTABLE) cd rust && cargo build

.PHONY: clean-rust
clean-rust:
	cd rust && cargo clean

.PHONY: build
build: build-py build-rust
