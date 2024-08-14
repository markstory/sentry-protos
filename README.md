# sentry-protos

An ongoing experiment / demo with using protos and gRPC and sentry.  Currently holds a few demo
schemas, but is not actively used in production.

https://www.notion.so/sentry/Protobuf-gRPC-schema-registry-7325ddca05dc49a5b05aa317c5dd1641

# Publishing protos

Use the `release` workflow in GitHub actions to create new releases. Each time a release is created, packages will be published for each supported language.

# Local development workflow

sentry-protos makes it easy to develop and test protobuf/grpc changes locally before making
pull requests.

You'll need a local clone of this repository to start.

## Python

From the root of `sentry-protos` run:

```shell
make build-py
```

Then in your application install the python bindings with pip.

```shell
# CWD is in your python application
pip install -e ../sentry-protos/py
```

As you make changes to proto files, you will need to regenerate bindings with `make build-py`.

## Rust

From the root of `sentry-protos` run:

```shell
make build-rust
```

Your application's `Cargo.toml` will need the following:

```toml
[dependencies]
sentry_protos = "0.1.0"

[patch.crates-io]
sentry_protos = { path = "../sentry-protos/rust/" }
```
