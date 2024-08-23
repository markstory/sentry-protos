#!/bin/bash
set -eu

# Configure git
git config user.email bot@getsentry.com
git config user.name getsentry-bot

# Cleanup repository after releases are created
git rm -r rust/src/*

# An empty lib.sh is required for cargo to run the generator.
touch rust/src/lib.rs
git add rust/src/lib.rs

git commit -m "Cleanup generated rust code"
git pull --rebase && git push
