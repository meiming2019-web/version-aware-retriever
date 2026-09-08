# Portfolio: Version-Aware RAG MVP

## Project summary

Version-Aware RAG is a measured technical-documentation retrieval and answering
system for the Pydantic 1.10.13 to 2.5.3 migration. It treats topical relevance
and version applicability as separate questions, preserves frozen source
provenance, and keeps reviewed labels outside runtime inputs. The project
compares BM25, dense retrieval, reciprocal rank fusion and cross-encoder
reranking on a fixed corpus of 34 evidence units. RRF achieved held-out
Recall@5 of 0.8111 and MRR of 0.8333 across 12 answerable questions within a
16-question, 544-pair reviewed benchmark. Negative results remain documented:
metadata tiering harmed topical order, and cross-encoder recall gains did not
generalize. A minimal generator consumes RRF Top 5 and returns cited support
or explicit insufficiency. An installable wheel, offline tests and frozen
experiment records make the system inspectable without claiming production
readiness or universal correctness.

## Resume bullets

- Built a version-aware technical RAG system combining BM25 and dense
  retrieval with RRF; achieved 0.81 Recall@5 and 0.83 MRR on a frozen
  16-query held-out benchmark with 544 human-reviewed query–evidence pairs.
- Designed retrieval–generation–evaluation isolation with immutable evidence
  provenance, source-linked citations, and explicit INSUFFICIENT_EVIDENCE
  handling, preventing reviewed labels from entering runtime retrieval or
  generation.
- Shipped an installable Python CLI and GitHub release with hash-verified
  packaged resources and 261 deterministic tests; validated clean
  installation and retrieval outside the source checkout.

This is a bounded RAG pipeline, not an autonomous agent. Human review was explicit
single-reviewer batch approval of AI-assisted annotations, not independent agreement.

## 30-second pitch

“I built a technical RAG system around the idea that relevant documentation can
still be wrong for your software version. I separated relevance from applicability,
froze the corpus and benchmark, and compared sparse, dense, fusion and reranking.
RRF was the strongest held-out method for evidence recall and MRR; the more complex
reranker did not generalize. The shipped CLI produces source-linked answers or
explicit insufficiency, with an honest boundary between retrieval metrics and
three small qualitative generation checks.”

## 2-minute pitch

“Pydantic migrations make a useful bounded case: an old passage can be misleading
for a target-version question, while a newer migration guide can validly explain
the old behavior. I froze official sources at two exact releases and assembled
34 inspectable evidence units with provenance back to physical lines and
companion examples. I kept document version distinct from behavior applicability.

The evaluation uses explicit query-specific review, not version inequality as a
negative label. There are 16 held-out questions and 544 reviewed pairs, with
separate development families but a shared corpus. I froze rankings before
scoring, and stopped method experimentation after the held-out run.

BM25 provides identifier matching, dense retrieval provides semantic matching,
and equal-weight RRF combines ranks without comparing incompatible score scales.
RRF reached 0.8111 Recall@5 and 0.8333 MRR. Positive applicability tiers sometimes
promoted unrelated passages; a cross-encoder reduced one wrong-version exposure
but lost held-out recall. I kept those failures visible and shipped plain RRF.

Generation takes exactly five passages, separates untrusted text from instructions,
validates citation IDs, and has an explicit insufficient-evidence contract. Two
supported examples and one absence example matched reviewed decisions, with
three valid citations total. That is qualitative evidence, not 100% accuracy.
I packaged immutable runtime data inside the wheel and tested it outside the
repository. The main limits are benchmark size, sparse negatives, uncalibrated
abstention and lack of production-scale evidence.”

## Technical deep dives

1. Source freezing: exact commits, hashes, license notices and offline verification.
2. Compound evidence: unchanged content, contribution mappings and precise citations.
3. Benchmark design: scoped invalidity, historical support, review gates and family isolation.
4. BM25/dense/RRF: tokenization, CLS pooling, normalization, deterministic ties and score scales.
5. Metadata failure: positive endpoint matches cannot establish query-relative invalidity.
6. Cross-encoder failure: candidate-depth limits versus ordering regressions and held-out discipline.
7. Grounding boundary: schema checks versus entailment, prompt injection and explicit abstention.
8. Distribution: resource pins, minimal wheel data, clean environments and verified TLS.

## Likely interviewer questions

**What is genuinely version-aware here?** The corpus preserves exact document
snapshots and historical passages, evaluation judges query-relative version
validity, and generation receives provenance and version-sensitive instructions.
The final retriever is content-only RRF—not a proven version-validity classifier.

**Why not use the newest documents exclusively?** Migration questions may need
source behavior, and a V2 passage may explicitly describe V1. Snapshot inequality
alone does not establish invalidity.

**Why did metadata reranking fail?** Coarse positive tiers overrode topical ranking.
On the development pilot, RRF Recall@5 fell from .8889 to .6111. Unreviewed corpus
assertions cannot express explicit query-relative negative applicability.

**Why reject Cross-Encoder as default?** Held-out Recall@5 fell from RRF .8111 to
.7028 and MRR from .8333 to .8160. It improved Recall@1 and moved the sole reviewed
negative outside Top 5, so it is a meaningful ablation—not universally worse.

**Did you avoid leakage?** Generation reads only query text, corpus and provenance.
Rankings were frozen before scoring. Families were split, but documents were shared;
AI-assisted, non-blind authoring and single-human review remain limitations.

**What do 3/3 checks prove?** Only decision agreement on three predeclared examples
and reviewed-positive status of three citations. Not every sentence's correctness,
calibrated abstention or factual accuracy. No LLM judge was used.

**Why is UFPR still 1?** Retrieval returns nonempty rankings for all four corpus-relative
unanswerable questions. Generation can abstain; this small qualitative check does
not replace a population-level sufficiency evaluation.

**What would production require?** Larger independently reviewed data, richer negatives,
latency/cost budgets, privacy and abuse controls, cache/index operations, drift
monitoring and a new benchmark for method changes. Those were outside this MVP;
there are no production-user or traffic claims.
