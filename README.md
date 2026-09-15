# agentic-project-bootstrap

A bootstrap kit: docs, templates, and a linter that a software project copies in, or is pointed
at, so a human and their AI agents — Claude Code, Codex, others — share one set of design docs,
one workflow, and one source of truth for progress. It fits new projects and existing
codebases, solo weekend builds and multi-agent, multi-phase efforts, by picking a profile and a
tier instead of assuming one fixed shape of project.

Read `BOOTSTRAP.md` for the idea in one page and pointers into the rest of the kit; or, if your
agent supports skills, invoke `skills/bootstrap/SKILL.md` and let it run the greenfield or
brownfield procedure as a guided conversation, one design doc per session with a human review
gate after each. Either way you end with the tier-appropriate files in place, a profile chosen,
and a first session ready to open.

The linter and generator, `tools/check_docs.py`, is Python 3.11+, standard library only: run
`python tools/check_docs.py --root <path-to-your-project>` to check a project, add `--fix` to
regenerate the four index files it owns, and see `tools/hooks/README.md` for wiring it into a
Stop hook, a pre-commit hook, or CI. The kit's own test suite runs with
`python -m pytest tools/tests -q`.
