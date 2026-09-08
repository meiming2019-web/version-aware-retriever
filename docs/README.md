# Documentation

[ARCHITECTURE.md](ARCHITECTURE.md) is the canonical description of the shipped
v0.1.x system. [HLD.md](HLD.md) is the initial design record, not a specification
of every current runtime behavior. Milestone documents preserve experiments and
history, including superseded proposals and unsuccessful attempts.

## Current system

- [Project overview, installation and results](../README.md)
- [Current architecture and engineering boundaries](ARCHITECTURE.md)
- [Portfolio and interview material](PORTFOLIO.md)
- [v0.1.2 release notes](releases/v0.1.2.md) and
  [preservation audit](releases/v0.1.2-preservation.md)

## Evaluation and reproduction

- [Contracts and benchmark semantics](M1.1.md)
- [Source acquisition](M1.2b.md), [evidence extraction](M1.2c.md), and
  [applicability audit](M1.2c-applicability-review.md)
- [Question design/splits](M1.3a-query-review.md), [judgment pilot](M1.3b-judgment-pilot.md),
  and [deterministic evaluator](M1.3c.md)
- [Held-out review](M2.6a-heldout-batch-review.md) and
  [frozen four-method results](M2.6b-heldout-results.md)
- [Grounded-generation qualitative evaluation](M3.1.md#frozen-outputs)

The root README shows how to score the existing frozen rankings without inference
or artifact writes. To reconstruct the recorded neural environment, use a separate
Python **3.12.7** environment and run from a source checkout:

```sh
python -m pip install -c constraints/frozen-eval.txt '.[dense,reranker]'
```

[These seven constraints](../constraints/frozen-eval.txt) come from the committed
Dense/Cross-Encoder `runtime.packages` records, corroborated by M2.1, M2.5 and
M2.6b. They are not a complete transitive lockfile or normal-user installation
requirement. Exact model revisions remain in the architecture and experiment
records; weights are external. Matching these versions cannot promise
bit-identical neural inference across hardware/platforms. This command only sets
up dependencies: it does **not** authorize rerunning or replacing frozen runs.

## Historical design and experiments

- [Initial HLD](HLD.md)
- M1: contracts, corpus and benchmark records linked above; [BM25 baseline](M1.3d.md)
- M2: [Dense](M2.1.md), [development review](M2.2.md),
  [development results](M2.2-results.md), [RRF](M2.3.md),
  [positive metadata tiers](M2.4.md), [Cross-Encoder](M2.5.md), and held-out records above
- [M3.1 engineering record](M3.1.md): prompt/schema, diagnostics, earlier blocked
  attempts and final frozen outputs; read its final outcome alongside the history
- Original release records: [v0.1.0](releases/v0.1.0.md), [v0.1.1](releases/v0.1.1.md)
