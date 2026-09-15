# Running check_docs automatically

`tools/check_docs.py` is meant to run without anyone remembering to run it.

## Claude Code Stop hook

Add to `.claude/settings.json` in the project (or `settings.local.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python tools/check_docs.py --root . || (echo 'check_docs found errors; fix them before ending the session' && exit 2)"
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
python tools/check_docs.py --root . || exit 1
```

## CI

Run `python tools/check_docs.py --root .` as a step. It exits 1 on any E-code.

## Regenerating indexes

`python tools/check_docs.py --root . --fix` rewrites `<project>/docs/milestones/README.md`, `<project>/docs/plans/README.md`, `<project>/docs/decisions/README.md`, and `<project>/docs/CURRENT.md`. Run it at the end of every session and commit the result. Never edit those four files by hand.
