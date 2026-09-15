# Running check_docs automatically

`tools/check_docs.py` is meant to run without anyone remembering to run it.

The snippets below call `python3`, the name on macOS and Debian-family Linux; Windows users
substitute `python`.

## Claude Code Stop hook

The hook receives Claude Code's JSON on stdin and should exit 0 when `stop_hook_active` is
true, so a session that cannot fix the errors is not blocked forever. `tools/hooks/stop.sh`
guards for that:

```sh
#!/bin/sh
input=$(cat)
case "$input" in *'"stop_hook_active": true'*) exit 0;; esac
python3 tools/check_docs.py --root . || { echo 'check_docs found errors; fix them before ending the session'; exit 2; }
```

Add to `.claude/settings.json` in the project (or `settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sh tools/hooks/stop.sh"
          }
        ]
      }
    ]
  }
}
```

Exit code 2 from a Stop hook blocks the stop and shows the message to the agent. Warnings do not block.

## Pre-commit hook

`.git/hooks/pre-commit` (make it executable), or the equivalent entry in your pre-commit framework:

```sh
#!/bin/sh
python3 tools/check_docs.py --root . || exit 1
```

## CI

Run `python3 tools/check_docs.py --root .` as a step. It exits 1 on any E-code.

## Regenerating indexes

`python3 tools/check_docs.py --root . --fix` rewrites `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`, `<project>/docs/decisions/README.md`, and `<project>/docs/CURRENT.md`. Run it at the end of every session and commit the result. Never edit those four files by hand.
