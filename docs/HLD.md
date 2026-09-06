# Version-Aware API & Dependency Compatibility Retriever

**Document Type:** High-Level Design
**Version:** v0.1
**Status:** Initial Design
**Primary Goal:** Portfolio-grade Retrieval / RAG system demonstrating reliable retrieval over versioned and conflicting technical knowledge

---

# 1. Overview

## 1.1 Problem

Software documentation is version-sensitive.

A developer may ask:

> Why did this API stop working after upgrading from version 1.x to 2.x?

A conventional semantic search or RAG system may retrieve documentation that is highly relevant in meaning but invalid for the user's software version.

For example:

* the API existed in v1.10;
* it was removed in v2.0;
* current v2.x documentation describes a replacement;
* an old GitHub issue still contains the deprecated solution.

All sources may be semantically relevant.

Only some are valid for the user's environment.

The central problem is therefore not:

> Can the system retrieve similar text?

It is:

> Can the system retrieve evidence that is both relevant and valid for the requested software version?

---

# 2. Project Thesis

The project studies the following question:

> **How can a retrieval-augmented AI system reliably answer software compatibility and migration questions when technical knowledge changes across versions?**

The main engineering focus is retrieval reliability rather than conversational UX.

The system should distinguish between:

* semantically relevant evidence;
* lexically relevant evidence;
* version-valid evidence;
* authoritative evidence;
* superseded evidence;
* misleading historical evidence.

The system should also recognize when no sufficiently valid evidence exists.

---

# 3. Initial Scope

## 3.1 Initial Ecosystem

The first supported ecosystem will be:

**Pydantic 1.x → Pydantic 2.x**

This provides a bounded but realistic domain containing:

* renamed APIs;
* removed APIs;
* changed validation behavior;
* migration documentation;
* version-specific reference documentation;
* release notes;
* examples;
* historical GitHub discussions.

The architecture should not assume Pydantic-specific behavior, but v0.1 will only claim validated support for this ecosystem.

---

# 4. Goals

The system should demonstrate the ability to:

1. Retrieve evidence using both lexical and semantic signals.
2. Distinguish exact technical identifiers from natural-language intent.
3. Respect requested library and version constraints.
4. Retrieve migration evidence across source and target versions.
5. Combine sparse and dense retrieval.
6. Rerank candidate evidence using richer query context.
7. prefer authoritative and temporally valid sources.
8. Detect and suppress wrong-version evidence.
9. Produce answers grounded in retrieved evidence.
10. Attach precise citations to claims.
11. Abstain when valid supporting evidence is unavailable.
12. Measure retrieval quality independently from answer quality.
13. Measure cases where retrieval improves or harms downstream answers.

---

# 5. Non-Goals

The project will NOT attempt to be:

* a universal coding assistant;
* an autonomous migration agent;
* a code repair agent;
* a general documentation chatbot;
* an IDE copilot;
* a multi-agent system;
* a production enterprise search platform;
* a system supporting arbitrary libraries;
* a source-code transformation engine;
* a model-training or fine-tuning project.

The system will not automatically modify user code.

The primary contribution is retrieval quality and evidence validity.

---

# 6. Primary User Scenarios

## 6.1 Breaking API Change

User asks:

> Why does `BaseModel.dict()` behave differently after upgrading from Pydantic v1 to v2?

The system should retrieve:

* relevant v1 behavior;
* migration documentation;
* relevant v2 behavior;
* any authoritative breaking-change documentation.

It should not answer exclusively from current documentation without explaining the version transition.

---

## 6.2 Renamed or Removed API

User asks:

> What replaced API X in Pydantic v2?

The system should prioritize migration and v2 reference documentation rather than a highly similar v1 tutorial.

---

## 6.3 Natural-Language Symptom

User asks:

> Why is serialization behaving differently after upgrading?

The query contains no exact API symbol.

Dense retrieval may therefore become more important than lexical retrieval.

The system should still use version information to prevent irrelevant current or historical documentation from dominating the result.

---

## 6.4 Exact Identifier Query

User asks:

> What happened to `parse_obj_as` in v2?

Exact identifiers are highly informative.

Sparse retrieval should strongly contribute to candidate generation.

---

## 6.5 Wrong-Version Hard Negative

User asks about v1.10.

A v2.x document is extremely semantically similar.

The system should identify the document as temporally incompatible rather than ranking it first solely because of semantic similarity.

---

## 6.6 Insufficient Evidence

User asks about behavior not covered by the indexed authoritative sources.

The system should be able to respond:

> Insufficient version-valid evidence was found.

It should not invent a migration explanation.

---

# 7. High-Level Architecture

```text
                     User Query
                         │
                         ▼
                Query Understanding
                         │
              ┌──────────┴──────────┐
              │                     │
        Technical Terms        Version Context
      API / error / concept    source / target
              │                     │
              └──────────┬──────────┘
                         ▼
                  Query Representation
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
   Sparse Retrieval              Dense Retrieval
      (lexical)                     (semantic)
          │                             │
          └──────────────┬──────────────┘
                         ▼
                     Fusion
                         │
                         ▼
              Metadata / Version Rules
                         │
                         ▼
                      Reranker
                         │
                         ▼
              Evidence Selection Layer
                         │
               ┌─────────┴─────────┐
               │                   │
          Valid Evidence      Invalid / Weak
               │                   │
               ▼                   ▼
         Context Builder         Suppress
               │
               ▼
              LLM
               │
               ▼
       Grounded Answer + Citations
               │
               ▼
        Validation / Abstention
```

---

# 8. Major Components

## 8.1 Corpus Ingestion

Responsible for transforming raw technical sources into retrievable evidence units.

Initial source classes may include:

* official API reference;
* migration guides;
* release notes;
* changelogs;
* official examples;
* selected GitHub issues or discussions.

Each source must preserve provenance.

The ingestion pipeline should avoid treating all documents as interchangeable text.

---

# 9. Evidence Model

Each retrievable unit should conceptually contain:

```text
Evidence Unit
├── content
├── library
├── version or version range
├── document type
├── source authority
├── source URL / provenance
├── section
├── technical identifiers
├── publication / release context
└── supersession information where available
```

Example:

```text
library: pydantic
version_range: >=2.0
document_type: migration_guide
authority: official
api_symbols:
  - model_dump
  - dict
section:
  - Changes to BaseModel
```

Version metadata is part of correctness, not merely search optimization.

---

# 10. Evidence Units and Chunking

The project should avoid treating arbitrary fixed-size text chunks as the only retrieval unit.

Technical documentation contains meaningful structures such as:

* API entries;
* headings;
* migration sections;
* examples;
* breaking-change entries;
* release-note items.

Whenever possible, retrieval units should preserve these semantic boundaries.

The project should later evaluate whether structure-aware evidence units outperform naive fixed-size chunks.

---

# 11. Query Understanding

The system should derive structured query context before retrieval.

Important attributes may include:

### Technical identifiers

Examples:

* class names;
* function names;
* configuration properties;
* error messages.

### Conceptual intent

Examples:

* serialization;
* validation;
* configuration;
* schema generation.

### Version context

Examples:

```text
current version = 1.10
target version = 2.0
```

or:

```text
requested version = 2.x
```

### Query type

Possible classes:

* behavior lookup;
* migration question;
* breaking-change diagnosis;
* compatibility question;
* replacement API lookup.

The purpose is not to build a complicated intent classifier.

The purpose is to expose information that materially affects retrieval.

---

# 12. Retrieval Strategy

## 12.1 Sparse Retrieval

Sparse retrieval is useful for:

* API names;
* class names;
* configuration fields;
* exception names;
* exact version numbers;
* exact error strings.

Example:

```text
BaseModel.model_dump
```

Exact lexical matching can carry more signal than semantic similarity.

---

## 12.2 Dense Retrieval

Dense retrieval is useful when the user's language differs from the documentation.

Example:

User:

> Why are None values serialized differently after upgrading?

Documentation:

> Changes to serialization behavior and exclusion parameters.

The texts differ lexically but are semantically related.

---

# 13. Hybrid Retrieval

Neither sparse nor dense retrieval is assumed to dominate universally.

Candidate evidence should therefore be collected from both systems.

Conceptually:

```text
Sparse Candidates
       +
Dense Candidates
       │
       ▼
     Fusion
       │
       ▼
Unified Candidate Set
```

The project should evaluate:

* sparse only;
* dense only;
* hybrid retrieval.

The winning strategy should be determined empirically rather than assumed.

---

# 14. Version and Metadata Validation

This is the defining capability of the system.

After candidate retrieval, each item should be evaluated against the query's compatibility context.

Possible outcomes include:

### Valid

The evidence directly applies to the requested version.

### Transition Evidence

The evidence explains a change between the source and target version.

### Related but Temporally Invalid

The evidence is semantically relevant but applies to a different version.

### Superseded

A more authoritative or newer source replaces the evidence.

### Unknown

Version applicability cannot be established reliably.

These states influence ranking and evidence selection.

---

# 15. Source Authority

Not all evidence sources should carry equal weight.

A conceptual authority hierarchy might be:

```text
Official migration guide
        ↓
Official API/reference documentation
        ↓
Official release notes / changelog
        ↓
Maintainer discussion
        ↓
GitHub issue
        ↓
Community discussion
```

This hierarchy should not blindly determine ranking.

However, authority becomes especially important when sources conflict.

---

# 16. Reranking

Initial retrieval should optimize candidate recall.

Reranking should optimize final relevance.

The reranking stage may consider:

* semantic relevance;
* exact technical identifiers;
* requested version;
* source and target versions;
* document type;
* source authority;
* migration relationship;
* temporal validity.

Example:

```text
Candidate A
semantic similarity: very high
version: wrong
authority: unofficial

Candidate B
semantic similarity: high
version: correct
authority: official migration guide
```

Candidate B should usually rank above Candidate A.

---

# 17. Context Selection

The final context sent to the LLM should not simply contain the highest-scoring chunks.

The system should aim to provide complementary evidence.

For a migration question, useful evidence may include:

```text
Old behavior
      +
Migration explanation
      +
New behavior
```

rather than three nearly identical current-version documents.

Duplicate and redundant evidence should therefore be controlled.

---

# 18. Answer Generation

Generation is intentionally a secondary layer.

The LLM should receive:

* the user question;
* normalized version context;
* selected evidence;
* provenance information.

The model should be instructed to:

1. distinguish old and new behavior;
2. avoid claims unsupported by retrieved evidence;
3. cite evidence for technical claims;
4. explicitly mention version applicability;
5. acknowledge uncertainty;
6. abstain when necessary.

---

# 19. Citation Model

A valid answer should make it possible to trace important claims back to evidence.

Example:

```text
In Pydantic v1, X behaved as ...
[Source A]

The v2 migration guide introduced ...
[Source B]

In v2, the supported replacement is ...
[Source C]
```

Citation validity is part of system evaluation.

A citation is not considered correct merely because the cited document discusses a similar topic.

It must support the associated claim and be valid for the relevant version.

---

# 20. Abstention

The system should support explicit non-answer behavior.

Possible abstention triggers include:

* no version-valid evidence;
* contradictory authoritative evidence;
* requested version outside supported corpus;
* insufficient evidence to establish compatibility;
* evidence only from low-authority sources.

The correct outcome may therefore be:

```text
NO_SUPPORTED_ANSWER
```

rather than a plausible-looking response.

---

# 21. Evaluation Strategy

Evaluation is a first-class subsystem.

The system should evaluate retrieval independently from generation.

---

# 22. Retrieval Evaluation

Candidate metrics include:

* Recall@K;
* Precision@K;
* MRR;
* nDCG;
* wrong-version retrieval rate;
* valid-evidence rate;
* authoritative-evidence rate.

Particular attention should be paid to:

> How often does the system retrieve persuasive but version-invalid evidence?

---

# 23. Query Categories

The benchmark should contain multiple query types.

Examples:

### Exact Identifier

Contains exact API symbol.

### Semantic Symptom

No exact symbol.

### Migration

Explicit source → target version.

### Wrong-Version Hard Negative

Near-identical evidence exists for an invalid version.

### Deprecated API

Old solutions remain easy to retrieve.

### Conflicting Sources

Older and newer documentation disagree.

### No Evidence

Correct behavior is abstention.

The system should report performance separately for different query classes where useful.

---

# 24. Retrieval Ablation

The project should support controlled comparisons such as:

```text
Dense only

vs

Sparse only

vs

Hybrid

vs

Hybrid + reranking

vs

Hybrid + reranking + version constraints
```

This is a central portfolio experiment.

The project should not assume every additional stage improves the system.

---

# 25. Downstream Evaluation

Higher retrieval metrics do not automatically imply better final answers.

The system should therefore measure downstream effects.

Questions include:

* Did correct evidence improve answer correctness?
* Did wrong-version evidence produce incorrect answers?
* Did reranking improve citation quality?
* Did stronger filtering reduce hallucinated migration advice?
* Did retrieval ever hurt performance compared with no retrieval?

This creates a distinction between:

```text
Retrieval quality
```

and:

```text
End-to-end answer quality
```

---

# 26. Hard Negatives

Hard negatives are a core part of the evaluation design.

Examples include:

### Same API, Wrong Version

Highly similar documentation exists for another version.

### Similar Symptom, Different Cause

The language is similar but the behavior changed for an unrelated reason.

### Deprecated Example

An old official example remains highly searchable.

### Newer Documentation

Current documentation is semantically excellent but invalid for historical behavior.

### Similar Name

Two technical concepts or APIs have overlapping names.

The purpose is to expose failure modes that a simple semantic search system may hide.

---

# 27. System Observability

For each query, the system should make retrieval decisions inspectable.

Useful trace information may include:

```text
query
parsed version context
sparse candidates
dense candidates
fusion scores
metadata decisions
reranking results
selected evidence
rejected evidence
citations
final answer status
latency
```

This enables investigation of retrieval failures.

---

# 28. Failure Modes

The project should explicitly study several failure categories.

## Retrieval Miss

Correct evidence is never retrieved.

## Ranking Failure

Correct evidence exists in the candidate set but ranks too low.

## Version Failure

Evidence is relevant but invalid for the requested version.

## Authority Failure

Low-authority evidence outranks stronger evidence.

## Redundancy Failure

The context contains multiple redundant pieces of evidence but misses required complementary evidence.

## Citation Failure

The answer cites a source that does not support the claim.

## Generation Failure

Correct evidence is available but the LLM interprets it incorrectly.

## Abstention Failure

The system answers despite insufficient valid evidence.

These categories should help distinguish where failures occur.

---

# 29. Performance Considerations

This is a portfolio system, not an internet-scale search engine.

Primary performance dimensions are:

* query latency;
* reranking latency;
* embedding cost;
* generation cost;
* corpus indexing time;
* number of retrieved candidates;
* number of LLM input tokens.

Latency and cost should be measured, but production-scale claims should not be made.

---

# 30. Security and Trust Boundary

External documents should be treated as untrusted evidence.

Retrieved content should not be interpreted as system instructions.

The architecture should conceptually separate:

```text
System instructions
        │
User query
        │
Retrieved untrusted evidence
```

The project does not need to become a security research project, but basic prompt-injection awareness should be preserved.

---

# 31. Expected Portfolio Contribution

The project should primarily prove competency in:

* retrieval engineering;
* embeddings;
* sparse retrieval;
* dense retrieval;
* hybrid search;
* metadata-aware retrieval;
* temporal reasoning;
* reranking;
* grounding;
* citation validation;
* retrieval evaluation;
* hard-negative construction;
* AI system reliability;
* backend-oriented AI system design.

It should NOT be marketed primarily as:

> “An AI chatbot for Pydantic documentation.”

---

# 32. Relationship to CI Failure Investigator

The two projects should remain technically and conceptually distinct.

## CI Failure Investigator

Primary question:

> How can an LLM-driven system investigate a CI failure using bounded tools and evidence?

Primary technical focus:

* agent orchestration;
* tool use;
* investigation state;
* hypothesis management;
* causal reasoning;
* evidence provenance;
* evaluation;
* reliability.

---

## Version-Aware Compatibility Retriever

Primary question:

> How can an AI system retrieve the correct technical evidence when knowledge changes across versions?

Primary technical focus:

* retrieval;
* ranking;
* metadata;
* version validity;
* source authority;
* citation;
* retrieval evaluation.

---

# 33. Shared Portfolio Narrative

The common theme is:

> **Reliable AI systems that make decisions from imperfect engineering evidence.**

The systems attack that problem differently:

```text
CI Failure Investigator
        │
        ▼
Reliable Investigation


Compatibility Retriever
        │
        ▼
Reliable Retrieval
```

This keeps the portfolio coherent without making the projects redundant.

---

# 34. Success Criteria for v0.1

The project can be considered portfolio-ready when it can credibly demonstrate:

1. A real versioned technical corpus.
2. A reproducible evaluation dataset.
3. Sparse retrieval baseline.
4. Dense retrieval baseline.
5. Hybrid retrieval.
6. Version-aware filtering or ranking.
7. Reranking.
8. Hard-negative evaluation.
9. Citation-grounded answers.
10. Abstention behavior.
11. Retrieval metrics.
12. At least one meaningful ablation study.
13. At least one documented retrieval failure.
14. Measured downstream answer impact.
15. Clear limitations.

The goal is not perfect performance.

The goal is to produce defensible engineering evidence about which retrieval strategies work, fail, and why.

---

# 35. Explicit v0.1 Boundaries

For the first portfolio version:

**Supported**

* Pydantic
* bounded set of 1.x / 2.x documentation
* compatibility and migration questions
* offline evaluation
* retrieval experiments
* grounded answer generation

**Not Supported**

* arbitrary Python packages
* live web search
* autonomous dependency upgrades
* automatic code modification
* IDE integration
* multi-agent workflows
* fine-tuning
* production deployment claims
* enterprise authentication
* large-scale distributed indexing

These boundaries should remain stable unless evaluation evidence shows that expansion is necessary.

---

# 36. Design Principle

The defining principle of the project is:

> **Relevant does not necessarily mean valid.**

A technically trustworthy retrieval system must understand not only what evidence resembles the user's question, but whether that evidence actually applies to the user's software environment.

That distinction is the central technical thesis of the project.
