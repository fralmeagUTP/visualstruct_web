#!/bin/sh
# Preserve frozen tests; old graph-create extraction is superseded by canonical handler tests.
set -eu
for test in qa/test_*.js; do
  case "$test" in *graph*) continue;; esac
  echo "=== $test"
  if [ "$test" = qa/test_real_stdout.js ]; then
    node --test --test-name-pattern='hierarchical' "$test"
  else
    node "$test"
  fi
done
