# js2proto

This package provides a CLI tool that can be used to convert JSONSchema documents into protobuf descriptions.

# Setup

```shell
cd js2proto
pip install -e .
```
# Usage

After placing your jsonschema in the desired destintation within the `proto` directory, you can use `js2proto` to create a proto file.

```shell
js2proto proto/sentry_protos/sentry/flags/v1/flags.schema.json
````

:warning: Schema files must have an extension of `.schema.json` :warning:
