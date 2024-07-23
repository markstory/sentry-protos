fn main() -> Result<(), Box<dyn std::error::Error>> {
    // TODO need to glob all the protos and build them all.
    tonic_build::configure()
        // .build_server(false)
        .out_dir("../rs")
        .compile(
            &["../src/sentry_protos/options/v1/options.proto"],
            &["../src"]
        )
        .unwrap();
    // Once protos are built, layer in client adapters.
    Ok(())
}
