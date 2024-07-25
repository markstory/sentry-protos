use glob::glob;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Compile rust code for all proto files.
    for entry in glob("../src/sentry_protos/**/*.proto").expect("Failed to read glob pattern") {
        if let Ok(path) = entry {
            tonic_build::configure()
                .out_dir("../rust/src")
                .compile(&[path], &["../src"])
                .unwrap();
        }
    }
    // Once protos are built, layer in client adapters.
    Ok(())
}
