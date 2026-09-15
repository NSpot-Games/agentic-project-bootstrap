# Data / ML

For projects centred on a dataset and a metric computed over it — a model, a scoring pipeline, an ML-driven feature — where the central artefact is data and the numbers measured on it, not a UI or a public API.

## 1. Fits when

The central artefact is datasets and the metrics computed over them.

## 2. Design docs

| File | Sections | Written at |
|---|---|---|
| `<project>/docs/design/<product>-design.md` | the problem statement and who consumes the output; the target metric and its threshold (the exit criteria); the baseline and existing approaches; constraints (latency, cost, fairness); non-goals for the first model | bootstrap |
| `<project>/docs/design/data-model.md` | principles (source of truth, what is derived); the dataset schema with an annotated example record; feature definitions and provenance; validation and data-quality rules; versioning of datasets and features | bootstrap |
| `<project>/docs/design/experiment-protocol.md` | the hypothesis and experiment design; the train/validation/test split policy; metrics and how they're computed; reproducibility requirements (seeds, environment); stopping rules and what counts as a negative result | bootstrap |
| `<project>/docs/design/architecture.md` | pipeline stages (ingest, train, evaluate, serve); the key interfaces as code; data flow with a latency and throughput budget; persistence (artifacts, checkpoints); testing strategy; a "decisions we're committing to" list | bootstrap |
| `<project>/docs/design/model-card.md` | intended use and out-of-scope use; a training-data summary; evaluation results (the eval runs); known limitations and failure modes; maintenance and retraining triggers | phase start |

The model card is written once a model exists to describe, per the phase-based rule in `core/long-horizon.md §3`; the other four are written at bootstrap because the metric, the schema, and the protocol have to exist before the first experiment runs.

## 3. Vocabulary

| Template word | This profile's word |
|---|---|
| feature | experiment |
| exit criteria | target metric with threshold |
| evidence | eval run |
| example instance | labelled sample set |

IDs stay `M<n>-<nn>` (`core/layers.md §1`); only the word used in prose changes. An experiment that closes with a negative result still closes `done` (`core/lifecycle.md §4`) — a negative result is evidence, not a failed feature.

## 4. Example instance and evidence

Example instance: one labelled sample set — a real, representative set of labelled examples in the dataset's actual schema, exercising phase 1's target metric. Evidence: eval runs — a full run of the experiment protocol against the labelled sample set, producing the target metric with its threshold, recorded whichever way the result came out.

## 5. Default tier and M0

Default tier: Standard (`core/tiers.md §3`). M0 is nearly always: fold the gaps the labelled sample set surfaced back into the data model, before running the first real experiment.

## 6. Suggested non-goals

Starting categories to confirm or replace during Brainstorm:

- Productionizing the model before an eval run clears the target metric's threshold.
- Online A/B testing before an offline eval run is convincing.
- Multi-model ensembling before a single model beats the stated baseline.
- Hyperparameter-search infrastructure before the first experiment protocol is written.

## 7. Profile-specific lessons

1. An experiment that closes with a negative result is still a closed experiment — resist the urge to keep it `in progress` until it succeeds.
2. Write the labelled sample set before the experiment protocol; it's this profile's version of the example instance, and surfaces the same class of gaps.
3. A target metric without a threshold is not an exit criterion; pick the number before running the first experiment.
