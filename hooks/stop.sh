#!/bin/sh
# Plugin-level Stop hook. Runs the project's own copy of the linter, and only in projects
# that have one, so repos not built on the kit are never linted.
input=$(cat)
case "$input" in *'"stop_hook_active": true'*) exit 0;; esac
root="${CLAUDE_PROJECT_DIR:-.}"
[ -f "$root/tools/check_docs.py" ] || exit 0
py=python3
command -v python3 >/dev/null 2>&1 || py=python
"$py" "$root/tools/check_docs.py" --root "$root" \
  || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
