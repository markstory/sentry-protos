#!/bin/bash
set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# shellcheck disable=SC2034
OLD_VERSION="$1"
NEW_VERSION="$2"

# Update VERSION file
echo "$NEW_VERSION" > VERSION

# Build rust code
# TODO(mark): This isn't great but I don't see another place I can hook into craft release
# cycle to generate the necessary code for rust.
make build-rust

# Update rust/Cargo.toml
perl -pi -e "s/^version = \".*?\"/version = \"$NEW_VERSION\"/" rust/Cargo.toml

echo "New version: $NEW_VERSION"
