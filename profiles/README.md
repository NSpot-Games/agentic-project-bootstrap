# Profiles

A profile chooses which design docs a project writes, what its templates call things, its default tier, what "example instance" and "evidence" mean for it, and what its first milestone nearly always does. Everything else — doc kinds, layers and IDs, tiers, lifecycle, long-horizon rules, parallel-agent rules, adoption — is shared machinery in `core/` that every profile sits on top of unchanged.

## 1. How to pick

Pick by asking what the project's central artefact is — the one thing that, if you got it right, the rest follows:

| The central artefact is... | Profile |
|---|---|
| Authored data — levels, cards, encounters, dialogue, itineraries — driving a runtime | `profiles/data-driven-product.md` |
| Tenants and the journeys they take through a shared product | `profiles/web-app-saas.md` |
| A public API surface other code calls | `profiles/library-sdk-cli.md` |
| Datasets and the metrics computed over them | `profiles/data-ml.md` |
| Environments and the SLOs they must hold | `profiles/infra-platform.md` |
| A question worth answering before committing to build anything | `profiles/research-prototype.md` |

If a project genuinely straddles two of these, pick the one that matches phase 1's central artefact and revisit at the next phase's design docs (`core/long-horizon.md §3`) — a profile choice is not permanent, but changing it mid-phase means redoing whichever design docs the new profile calls for and the old one didn't.

## 2. What every profile shares

A profile plugs into machinery it does not redefine:

- **Document kinds** (`core/doc-kinds.md`) — design, decision, direction, progress, reference, and the rules that keep each trustworthy.
- **Layers and identifiers** (`core/layers.md`) — phase, milestone, feature, plan, and their ID rules. `M<n>` and `M<n>-<nn>` never change meaning between profiles; only the word a profile's templates use for "milestone" or "feature" in prose might.
- **Tiers** (`core/tiers.md`) — Lite, Standard, Full. A profile names a default; the project can still promote or start elsewhere.
- **Lifecycle** (`core/lifecycle.md`) — Ground, Brainstorm, Plan, Execute, Close, and the escape hatches (spikes, small changes).
- **Long-horizon rules** (`core/long-horizon.md`) — the rolling wave, phase exits, and when per-area design docs get written.
- **Parallel agents** (`core/parallel-agents.md`) — claiming, generated files, per-milestone plan directories.
- **Adoption** (`core/adoption.md`) — greenfield and brownfield procedures; `core/adoption.md §1`'s C0 step is where the tier and profile get decided.

## 3. The seven-section contract

Every profile file (`profiles/<name>.md`) carries exactly these seven numbered `## ` sections, in this order, and no others — `core/adoption.md` and `skills/bootstrap/SKILL.md` point at them by number, so the order and count are fixed:

1. **Fits when** — one or two sentences on the kind of project this profile suits.
2. **Design docs** — a table: file, section outline, written at bootstrap or at phase start (`core/long-horizon.md §3`).
3. **Vocabulary** — a table: the word the templates use → the word this profile's projects use instead.
4. **Example instance and evidence** — what a complete example instance is for this profile, and what counts as evidence at a milestone's exit.
5. **Default tier and M0** — which tier (`core/tiers.md §1`) a project on this profile starts at, and what its first milestone (`M0`) nearly always does.
6. **Suggested non-goals** — categories of work this kind of project tends to over-build early; a starting point for the design doc's non-goals section, not a mandate.
7. **Profile-specific lessons** — lessons for bootstrapping this kind of project, in the spirit of `core/lessons.md` but specific to this profile.

## 4. Profiles at a glance

| Profile | Fits when | Default tier |
|---|---|---|
| `profiles/data-driven-product.md` | Authored data drives a runtime | Standard |
| `profiles/web-app-saas.md` | Tenants and journeys through a shared product | Standard |
| `profiles/library-sdk-cli.md` | A public API surface other code calls | Standard |
| `profiles/data-ml.md` | Datasets and metrics over them | Standard |
| `profiles/infra-platform.md` | Environments and the SLOs they hold | Standard |
| `profiles/research-prototype.md` | A question worth answering before building | Lite |
