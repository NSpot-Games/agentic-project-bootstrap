#!/bin/sh
input=$(cat)
py=python3
"$py" -c "pass" >/dev/null 2>&1 || py=python
if printf '%s' "$input" | "$py" -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("stop_hook_active") else 1)' 2>/dev/null; then exit 0; fi
"$py" tools/check_docs.py --root . || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
