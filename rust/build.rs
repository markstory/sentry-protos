use std::path::PathBuf;

use std::fs;
use std::fs::File;
use std::io::Write;
use std::str;
use glob::glob;
use regex::Regex;

#[derive(Clone, Debug)]
struct ModuleInfo {
    name: String,
    path: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // collect module names
    let mut module_metadata = Vec::new();

    // Compile rust code for all proto files.
    for entry in glob("../proto/sentry_protos/**/*.proto").expect("Failed to read glob pattern") {
        if let Ok(path) = entry {
            module_metadata.push(get_module_info(&path));

            // TODO this doesn't currently handle the options/v1/ path
            // correctly. Only topics.proto is saved, options.proto
            // is lost.
            tonic_build::configure()
                .out_dir("../rust/src")
                .compile(&[path], &["../proto"])
                .unwrap();
        }
    }

    let mut visited: Vec<&str> = vec![];
    let mut lib_rs = String::new();
    for module in module_metadata.iter() {
        if visited.iter().any(|i| i.contains(&module.name)) {
            continue;
        }
        visited.push(module.name.as_str());

        // TODO find a better way to generate this code
        lib_rs.push_str("#[path = \"\"]\n");
        lib_rs.push_str(format!("pub mod {} {{\n", module.name).as_ref());
        lib_rs.push_str(format!("    #[path = \"{}.rs\"]\n", module.path).as_ref());
        lib_rs.push_str("    pub mod v1;\n");
        lib_rs.push_str("}\n");
        lib_rs.push_str("\n");
    }

    // Generate lib.rs with the proto modules.
    let mut lib_file = File::create("src/lib.rs").unwrap();
    lib_file.write_all(lib_rs.as_bytes()).expect("Failed to write lib.rs");

    // Once protos are built, layer in client adapters.
    Ok(())
}

fn get_module_info(path: &PathBuf) -> ModuleInfo {
    let file = fs::read(path);
    let Ok(contents) = file else {
        panic!("Could not read {:?}", path);
    };
    let contents_str = str::from_utf8(&contents).unwrap();
    let pattern = Regex::new(r"(?m)^package\s+(?<name>[^;]+);").unwrap();
    let Some(captures) = pattern.captures(contents_str) else {
        panic!("Could not find package name in {:?}", path);
    };
    let package_name = captures["name"].to_string();
    let mut parts = package_name.split('.');
    let name = parts.nth_back(1).unwrap().to_string();

    ModuleInfo {name: name, path: package_name}
}
