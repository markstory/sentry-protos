# Rust binding generator

This package provides a command line tool for generating
rust bindings. Using `build.rs` proved problematic in our craft/publish flow.

# Generating bindings

```shell
cargo run -p rustgenerator
```

The above will regenerate rust binding package that can be published separately.
