#!/bin/sh
input=$(cat)
case "$input" in *'"stop_hook_active": true'*) exit 0;; esac
python3 tools/check_docs.py --root . || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
