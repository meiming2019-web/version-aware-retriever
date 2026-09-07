"""Review-gated four-question development pilot; never scores draft judgments."""

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from version_aware_retriever.acquisition import decode_record, digest, require
from version_aware_retriever.contracts import (
    Answerability,
    ApplicabilityAssertion,
    AssertionKind,
    Benchmark,
    BenchmarkQuery,
    ContributionRole,
    EvidenceRole,
    EvidenceUnit,
    GoldJudgment,
    QueryCategory,
    RankedResult,
    RankedRun,
    ReviewStatus,
    SelectorKind,
    SourceContribution,
    SourceManifestEntry,
    VersionApplicability,
    VersionSelector,
)
from version_aware_retriever.evaluation import CUTOFFS, evaluate
from version_aware_retriever.lexical import (
    RetrievalQuery,
    canonical,
    documents_from_artifact,
    project_queries,
    queries_from_public,
)

PILOT_IDS = ("q:a7c2", "q:39fa", "q:7bd4", "q:b503")
PATHS = {
    "pilot": "data/pydantic/benchmark/judgments.dev-pilot.draft.json",
    "development_queries": "data/pydantic/benchmark/queries.dev.draft.json",
    "public_queries": "data/pydantic/benchmark/queries.dev.input.json",
    "evidence": "data/pydantic/extraction/derived/evidence.json",
    "manifest": "data/pydantic/frozen/manifest.json",
    "labeling_policy": "docs/M1.3b-judgment-pilot.md",
}
DECISIONS = "data/pydantic/benchmark/dev-pilot.review-decisions.json"
RUNS = (
    "data/pydantic/runs/bm25.dev.unscored.json",
    "data/pydantic/runs/dense.dev.unscored.json",
)
FORMAT = "development-pilot-review-v1"
LABEL_FIELDS = {
    "topical_relevance",
    "version_applicability",
    "evidence_roles",
    "hard_negative",
}


def read_json(path: Path) -> Any:
    return decode_json(path.read_bytes())


def decode_json(body: bytes) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    return json.loads(body, object_pairs_hook=unique)


def version(data: dict[str, Any]) -> VersionSelector:
    return VersionSelector(**{**data, "kind": SelectorKind(data["kind"])})


def evidence_record(data: dict[str, Any]) -> EvidenceUnit:
    assertions = []
    for row in data["applicability"]:
        assertions.append(
            ApplicabilityAssertion(
                **{
                    **row,
                    "kind": AssertionKind(row["kind"]),
                    **{
                        key: tuple(version(v) for v in row[key])
                        for key in (
                            "applies_to",
                            "transition_source",
                            "transition_target",
                        )
                    },
                }
            )
        )
    return EvidenceUnit(
        **{
            **data,
            "applicability": tuple(assertions),
            "section_path": tuple(data["section_path"]),
            "technical_identifiers": tuple(data.get("technical_identifiers", [])),
            "contributions": tuple(
                SourceContribution(**{**row, "role": ContributionRole(row["role"])})
                for row in data.get("contributions", [])
            ),
        }
    )


def judgment_record(data: dict[str, Any]) -> GoldJudgment:
    return GoldJudgment(
        **{
            **data,
            "version_applicability": VersionApplicability(
                data["version_applicability"]
            ),
            "evidence_roles": tuple(EvidenceRole(r) for r in data["evidence_roles"]),
            "review_status": ReviewStatus(data["review_status"]),
            "supporting_locators": tuple(data["supporting_locators"]),
        }
    )


def locators(values: list[str] | tuple[str, ...], unit: EvidenceUnit) -> None:
    require(bool(values), "source-grounded locators required")
    for value in values:
        match = re.fullmatch(r"chars:(\d+):(\d+)", value)
        require(match is not None, "expected assembled chars:start:end locator")
        assert match is not None
        start, end = map(int, match.groups())
        require(0 <= start < end <= len(unit.content), "locator out of bounds")


@dataclass(frozen=True)
class Pilot:
    bindings: dict[str, str]
    sources: tuple[SourceManifestEntry, ...]
    evidence: tuple[EvidenceUnit, ...]
    public: tuple[RetrievalQuery, ...]
    curation: dict[str, dict[str, Any]]
    proposals: tuple[GoldJudgment, ...]
    issues: dict[tuple[str, str], list[str]]
    snapshot: str


def load_pilot(root: Path) -> Pilot:
    bodies = {name: (root / path).read_bytes() for name, path in PATHS.items()}
    bindings = {name: digest(body) for name, body in bodies.items()}
    data = {
        name: decode_json(body)
        for name, body in bodies.items()
        if name != "labeling_policy"
    }
    draft, pilot = data["development_queries"], data["pilot"]
    require(draft["split"] == "dev", "development inputs required")
    for artifact in (draft, pilot):
        require(
            artifact["review_status"] == "draft"
            and artifact["human_review_status"] == "pending",
            "original draft changed",
        )
    require(
        pilot["artifact_bindings"]
        == {
            PATHS["development_queries"]: bindings["development_queries"],
            PATHS["evidence"]: bindings["evidence"],
        },
        "stale pilot bindings",
    )
    require(
        draft["artifact_bindings"][PATHS["evidence"]] == bindings["evidence"],
        "stale development evidence binding",
    )
    require(
        project_queries(draft) == data["public_queries"], "public/draft query mismatch"
    )
    public = queries_from_public(data["public_queries"])
    require(
        len(public) == 8 and set(PILOT_IDS) <= {q.query_id for q in public},
        "expected eight public questions with four pilot IDs",
    )
    require(tuple(pilot["query_ids"]) == PILOT_IDS, "unexpected pilot questions")
    units = tuple(evidence_record(row["record"]) for row in data["evidence"]["units"])
    known = {u.evidence_id: u for u in units}
    require(len(units) == len(known) == 34, "expected 34 unique evidence IDs")
    sources = tuple(decode_record(row["record"]) for row in data["manifest"]["sources"])
    registry = {s.source_id: s for s in sources}
    require(len(registry) == len(sources), "duplicate source IDs")
    for unit in units:
        require(
            digest(unit.content.encode()) == unit.content_hash, "content hash mismatch"
        )
        for sid in {unit.source_id} | {c.source_id for c in unit.contributions}:
            require(
                sid in registry and registry[sid].ecosystem_id == unit.ecosystem_id,
                "unknown source or ecosystem mismatch",
            )
    require(
        data["evidence"]["selection_hash"] == data["manifest"]["selection_hash"],
        "selection binding mismatch",
    )
    proposals = tuple(judgment_record(row["judgment"]) for row in pilot["judgments"])
    pairs = {(j.query_id, j.evidence_id) for j in proposals}
    require(
        len(proposals) == len(pairs) == 136
        and pairs == {(q, e) for q in PILOT_IDS for e in known},
        "incomplete or duplicate pilot matrix",
    )
    for judgment in proposals:
        require(
            judgment.review_status is ReviewStatus.DRAFT, "proposal must remain draft"
        )
        locators(judgment.supporting_locators, known[judgment.evidence_id])
    issues = {}
    for row in pilot["judgments"]:
        require(row["human_review_status"] == "pending", "proposal wrapper changed")
        j = row["judgment"]
        issues[j["query_id"], j["evidence_id"]] = row["unresolved_issues"]
    documents = sorted(
        documents_from_artifact(data["evidence"]), key=lambda d: d.evidence_id
    )
    snapshot = (
        "retrieval-input:"
        + digest(
            canonical(
                {
                    "documents": [asdict(d) for d in documents],
                    "queries": [asdict(q) for q in public],
                }
            )
        )[7:]
    )
    return Pilot(
        bindings,
        sources,
        units,
        public,
        {
            row["retriever_input"]["query_id"]: row["curation"]
            for row in draft["queries"]
        },
        proposals,
        issues,
        snapshot,
    )


def text(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label} required")


def review(
    pilot: Pilot, decisions: dict[str, Any]
) -> tuple[dict[str, Any], tuple[BenchmarkQuery, ...], tuple[GoldJudgment, ...]]:
    require(
        set(decisions)
        == {
            "format",
            "status",
            "bindings",
            "question_decisions",
            "pair_decisions",
            "unresolved_issues",
        },
        "unexpected sidecar fields",
    )
    require(decisions["format"] == FORMAT, "unsupported review format")
    require(decisions["bindings"] == pilot.bindings, "stale review bindings")
    require(decisions["status"] in ("pending", "reviewed"), "invalid review status")
    require(isinstance(decisions["unresolved_issues"], list), "issues must be a list")
    unresolved = list(decisions["unresolved_issues"])
    for issue in unresolved:
        text(issue, "issue")
    known = {e.evidence_id: e for e in pilot.evidence}
    public = {q.query_id: q for q in pilot.public}
    questions: dict[str, BenchmarkQuery] = {}
    judgments: dict[tuple[str, str], GoldJudgment] = {}
    proposals = {(j.query_id, j.evidence_id): j for j in pilot.proposals}

    def common(row: dict[str, Any]) -> None:
        require(
            row["status"] == "reviewed",
            "omit pending decisions; only explicit review entries",
        )
        text(row["reviewer"], "actual reviewer")
        text(row["rationale"], "review rationale")
        require(isinstance(row["unresolved_issues"], list), "issues must be a list")
        for issue in row["unresolved_issues"]:
            text(issue, "issue")
            unresolved.append(issue)

    for row in decisions["question_decisions"]:
        require(
            set(row)
            == {
                "query_id",
                "status",
                "reviewer",
                "answerability",
                "rationale",
                "reviewed_all_evidence",
                "supporting_evidence",
                "unresolved_issues",
            },
            "unexpected question decision fields",
        )
        common(row)
        qid = row["query_id"]
        require(
            qid in PILOT_IDS and qid not in questions,
            "unknown or duplicate question decision",
        )
        require(
            row["reviewed_all_evidence"] is True,
            "question decision requires whole-corpus review",
        )
        answer = Answerability(row["answerability"])
        require(
            isinstance(row["supporting_evidence"], list),
            "supporting evidence must be a list",
        )
        for ref in row["supporting_evidence"]:
            require(
                set(ref) == {"evidence_id", "locator"} and ref["evidence_id"] in known,
                "unknown question supporting evidence",
            )
            locators([ref["locator"]], known[ref["evidence_id"]])
        require(
            answer is Answerability.UNANSWERABLE or bool(row["supporting_evidence"]),
            "answerable decision needs source grounding",
        )
        questions[qid] = BenchmarkQuery(
            **{
                **asdict(public[qid]),
                "requested_version": public[qid].requested_version,
                "source_version": public[qid].source_version,
            },
            primary_category=QueryCategory(pilot.curation[qid]["primary_category"]),
            answerability=answer,
            answerability_reason=row["rationale"],
        )

    for row in decisions["pair_decisions"]:
        require(
            set(row)
            == {
                "query_id",
                "evidence_id",
                "status",
                "reviewer",
                "action",
                "correction",
                "rationale",
                "supporting_locators",
                "issue_resolution",
                "unresolved_issues",
            },
            "unexpected pair decision fields",
        )
        common(row)
        pair = (row["query_id"], row["evidence_id"])
        require(
            pair in proposals and pair not in judgments,
            "unknown or duplicate pair decision",
        )
        patch = row["correction"]
        require(
            isinstance(patch, dict) and set(patch) <= LABEL_FIELDS,
            "unauthorized correction fields",
        )
        require(row["action"] in ("confirm", "correct"), "invalid decision action")
        require(
            (row["action"] == "correct") == bool(patch),
            "contradictory correction/action",
        )
        require(isinstance(row["supporting_locators"], list), "locators must be a list")
        locators(row["supporting_locators"], known[pair[1]])
        text_resolution = row["issue_resolution"]
        require(
            text_resolution is None or isinstance(text_resolution, str),
            "invalid issue resolution",
        )
        if pilot.issues[pair] and not (text_resolution and text_resolution.strip()):
            unresolved.extend(f"{pair[0]} / {pair[1]}: {s}" for s in pilot.issues[pair])
        original = asdict(proposals[pair])
        require(
            not patch
            or any(canonical(original[k]) != canonical(v) for k, v in patch.items()),
            "correction must change a label",
        )
        judgments[pair] = judgment_record(
            {
                **original,
                **patch,
                "rationale": row["rationale"],
                "supporting_locators": row["supporting_locators"],
                "review_status": "reviewed",
            }
        )
    for pair, issues in pilot.issues.items():
        if pair not in judgments:
            unresolved.extend(f"{pair[0]} / {pair[1]}: {s}" for s in issues)
    complete = len(questions) == 4 and len(judgments) == 136
    require(
        decisions["status"] != "reviewed" or complete,
        "reviewed sidecar has missing decisions",
    )
    if complete:
        for qid, query in questions.items():
            positive = any(
                j.query_id == qid and j.is_valid_positive for j in judgments.values()
            )
            require(
                positive == (query.answerability is Answerability.ANSWERABLE),
                f"{qid}: answerability conflicts with complete reviewed matrix",
            )
    ready = complete and not unresolved and decisions["status"] == "reviewed"
    return (
        {
            "bindings": pilot.bindings,
            "question_decisions": {
                "reviewed": len(questions),
                "pending": 4 - len(questions),
            },
            "pair_decisions": {
                "reviewed": len(judgments),
                "pending": 136 - len(judgments),
            },
            "unresolved_issues": unresolved,
            "sidecar_status": decisions["status"],
            "scoring_permitted": ready,
        },
        tuple(questions[q] for q in PILOT_IDS if q in questions),
        tuple(judgments[p] for p in sorted(judgments)),
    )


def reviewed_benchmark(pilot: Pilot, decisions: dict[str, Any]) -> Benchmark:
    readiness, queries, judgments = review(pilot, decisions)
    require(
        readiness["scoring_permitted"],
        "formal scoring blocked: human review incomplete or unresolved",
    )
    revision = (
        "development-pilot:"
        + digest(
            canonical(
                {
                    "bindings": pilot.bindings,
                    "decisions": decisions,
                }
            )
        )[7:]
    )
    return Benchmark(
        benchmark_revision=revision,
        sources=pilot.sources,
        evidence=pilot.evidence,
        queries=queries,
        judgments=judgments,
    )


def saved_results(pilot: Pilot, body: bytes) -> tuple[RankedResult, ...]:
    """Check saved-run compatibility without gold, review promotion, or scoring."""
    data = decode_json(body)
    require(data["status"] == "unscored", "expected original unscored run")
    require(
        data["retrieval_input_snapshot"] == pilot.snapshot,
        "run input snapshot mismatch",
    )
    require(
        data["artifact_hashes"]
        == {
            "evidence": pilot.bindings["evidence"],
            "public_queries": pilot.bindings["public_queries"],
        },
        "run input hashes mismatch",
    )
    results = tuple(
        RankedResult(query_id=r["query_id"], evidence_ids=tuple(r["evidence_ids"]))
        for r in data["results"]
    )
    require(
        len(results) == 8
        and {r.query_id for r in results} == {q.query_id for q in pilot.public},
        "missing or duplicate run queries",
    )
    known = {e.evidence_id for e in pilot.evidence}
    require(all(set(r.evidence_ids) <= known for r in results), "unknown result IDs")
    diagnostics = data["diagnostics"]
    require(
        len(diagnostics) == 8
        and {d["query_id"] for d in diagnostics} == {r.query_id for r in results},
        "invalid run diagnostics",
    )
    scores = {d["query_id"]: d["scores"] for d in diagnostics}
    for result in results:
        require(
            len(scores[result.query_id]) == len(result.evidence_ids)
            and all(
                type(x) in (float, int) and math.isfinite(x)
                for x in scores[result.query_id]
            ),
            "invalid aligned run scores",
        )
    text(data["run_id"], "original run ID")
    text(data["configuration"]["return_policy"], "declared return policy")
    return results


def adapt_run(pilot: Pilot, benchmark: Benchmark, body: bytes) -> RankedRun:
    results = saved_results(pilot, body)
    data = decode_json(body)
    run = RankedRun(
        run_id="development-pilot-run:"
        + digest(
            canonical(
                {
                    "benchmark": benchmark.benchmark_revision,
                    "original_run_id": data["run_id"],
                    "original_run_hash": digest(body),
                }
            )
        )[7:],
        benchmark_revision=benchmark.benchmark_revision,
        method_description=f"Original {data['run_id']} ({digest(body)}); "
        + data["configuration"]["return_policy"],
        results=tuple(next(r for r in results if r.query_id == q) for q in PILOT_IDS),
    )
    run.validate_against(benchmark)
    return run


def score(
    pilot: Pilot, decisions: dict[str, Any], runs: tuple[bytes, ...]
) -> dict[str, Any]:
    benchmark = reviewed_benchmark(pilot, decisions)
    adapted = tuple(adapt_run(pilot, benchmark, body) for body in runs)
    require(
        bool(adapted) and len({r.run_id for r in adapted}) == len(adapted),
        "duplicate or empty runs",
    )
    return {
        "scope": "four-question development pilot; not held-out evaluation",
        "limitations": "Only one proposed wrong-version behavior family; does not "
        "satisfy the original negative-coverage target or establish generalization. "
        "UFPR measures declared return policies, not calibrated rejection.",
        "bindings": pilot.bindings,
        "reviewed_pilot": {
            "benchmark_revision": benchmark.benchmark_revision,
            "evidence_ids": [e.evidence_id for e in benchmark.evidence],
            "queries": [asdict(q) for q in benchmark.queries],
            "judgments": [asdict(j) for j in benchmark.judgments],
        },
        "runs": [
            {
                "original_run_id": decode_json(body)["run_id"],
                "original_run_hash": digest(body),
                "adapted_run": asdict(run),
                "evaluation": asdict(evaluate(benchmark, run)),
            }
            for run, body in zip(adapted, runs, strict=True)
        ],
    }


def result_bytes(pilot: Pilot, decisions: bytes, runs: tuple[bytes, ...]) -> bytes:
    """Retain existing scores with deterministic provenance; no new metrics."""
    result = score(pilot, decode_json(decisions), runs)
    result.update(
        {
            "format_version": 1,
            "status": "reviewed-development-pilot",
            "review_decisions_hash": digest(decisions),
            "evaluator": {
                "source_hash": digest(
                    Path(__file__).with_name("evaluation.py").read_bytes()
                ),
                "contracts_hash": digest(
                    Path(__file__).with_name("contracts.py").read_bytes()
                ),
                "cutoffs": list(CUTOFFS),
                "mrr": "full-submitted-list; answerable-query macro mean",
                "recall": (
                    "version-valid evidence-unit recall; answerable-query macro mean"
                ),
                "wrong_version_rate": (
                    "item-weighted directly relevant version-invalid returns"
                ),
                "ufpr": (
                    "nonempty accepted list on corpus-relative unanswerable questions"
                ),
            },
        }
    )
    result["result_id"] = "development-pilot-result:" + digest(canonical(result))[7:]
    return (
        json.dumps(
            result, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def save_result(path: Path, body: bytes) -> None:
    require(
        not any(p.is_symlink() for p in (path, *path.parents)), "result path symlink"
    )
    if path.exists() and path.read_bytes() == body:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("readiness", "score"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--save",
        action="store_true",
        help="Retain the score at the fixed development-results path",
    )
    parser.add_argument(
        "--include-hybrid",
        action="store_true",
        help="Score the frozen RRF run too; save a separate three-method result",
    )
    args = parser.parse_args()
    require(not args.save or args.command == "score", "--save requires score")
    require(
        not args.include_hybrid or args.command == "score",
        "--include-hybrid requires score",
    )
    pilot = load_pilot(args.root)
    decision_bytes = (args.root / DECISIONS).read_bytes()
    decisions = decode_json(decision_bytes)
    if args.command == "readiness":
        result = review(pilot, decisions)[0]
    else:
        # Gate before even reading saved retrieval results.
        reviewed_benchmark(pilot, decisions)
        runs = tuple((args.root / p).read_bytes() for p in RUNS)
        result_name = "dev-pilot.bm25-vs-dense.json"
        if args.include_hybrid:
            hybrid = (
                args.root / "data/pydantic/runs/rrf-hybrid.dev.unscored.json"
            ).read_bytes()
            expected_sources = [
                {
                    "method": method,
                    "run_id": decode_json(source)["run_id"],
                    "content_hash": digest(source),
                }
                for method, source in zip(("bm25", "dense"), runs, strict=True)
            ]
            require(
                decode_json(hybrid)["source_runs"] == expected_sources,
                "hybrid lineage does not match submitted source runs",
            )
            runs = (*runs, hybrid)
            result_name = "dev-pilot.bm25-vs-dense-vs-hybrid.json"
        body = result_bytes(pilot, decision_bytes, runs)
        if args.save:
            save_result(args.root / "data/pydantic/results" / result_name, body)
        print(body.decode("utf-8"), end="")
        return
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
