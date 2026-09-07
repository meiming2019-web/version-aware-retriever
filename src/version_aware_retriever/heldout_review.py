"""Fixed held-out gold readiness only; no retrieval or scoring command."""

import argparse
import json
from pathlib import Path
from typing import Any

from version_aware_retriever.acquisition import decode_record, digest, require
from version_aware_retriever.contracts import Answerability, QueryCategory, ReviewStatus
from version_aware_retriever.lexical import project_queries, queries_from_public
from version_aware_retriever.pilot_evaluation import (
    Pilot,
    decode_json,
    evidence_record,
    judgment_record,
    locators,
    review,
)

QUERY_HASH = "sha256:ae091d32f903f4f0b4d783b501aa2f1cf754fad89247c64974ccf489df53a673"
PATHS = {
    "evaluation_queries": "data/pydantic/benchmark/queries.eval.draft.json",
    "development_queries": "data/pydantic/benchmark/queries.dev.draft.json",
    "evidence": "data/pydantic/extraction/derived/evidence.json",
    "manifest": "data/pydantic/frozen/manifest.json",
    "labeling_policy": "docs/M1.3b-judgment-pilot.md",
    "approved_policy_decisions": (
        "data/pydantic/benchmark/dev-pilot.review-decisions.json"
    ),
    "draft": "data/pydantic/benchmark/judgments.eval.draft.json",
}
DECISIONS = "data/pydantic/benchmark/eval.review-decisions.json"


def contamination_guard(root: Path, *, evaluation: bool = False) -> None:
    """Inspect filenames only; unexpected artifacts stop review before any reads."""
    allowed = {
        "runs": {
            "bm25.dev.unscored.json",
            "dense.dev.unscored.json",
            "rrf-hybrid.dev.unscored.json",
            "version-aware-rrf.dev.unscored.json",
            "cross-encoder-reranked.dev.unscored.json",
        },
        "results": {
            "dev-pilot.bm25-vs-dense.json",
            "dev-pilot.bm25-vs-dense-vs-hybrid.json",
            "dev-pilot.bm25-vs-dense-vs-hybrid-vs-version-aware.json",
            "dev-pilot.with-cross-encoder.json",
        },
    }
    if evaluation:
        allowed["runs"].update(
            {
                "bm25.eval.unscored.json",
                "dense.eval.unscored.json",
                "rrf-hybrid.eval.unscored.json",
                "cross-encoder-reranked.eval.unscored.json",
            }
        )
        allowed["results"].add("heldout.four-methods.json")
    for folder, names in allowed.items():
        base = root / "data/pydantic" / folder
        unexpected = [
            str(p.relative_to(base))
            for p in base.rglob("*")
            if p.is_file() and str(p.relative_to(base)) not in names
        ]
        require(
            not unexpected,
            f"contamination risk: unexpected {folder} artifacts: {unexpected}",
        )


def load_heldout(
    root: Path, *, evaluation: bool = False
) -> tuple[Pilot, dict[str, Any]]:
    contamination_guard(root, evaluation=evaluation)
    bodies = {name: (root / path).read_bytes() for name, path in PATHS.items()}
    bindings = {name: digest(body) for name, body in bodies.items()}
    require(
        bindings["evaluation_queries"] == QUERY_HASH,
        "authored held-out revision changed",
    )
    data = {k: decode_json(v) for k, v in bodies.items() if k != "labeling_policy"}
    draft, queries, dev = (
        data["draft"],
        data["evaluation_queries"],
        data["development_queries"],
    )
    require(queries["split"] == "eval" and dev["split"] == "dev", "split mismatch")
    for original in (draft, queries):
        require(
            original["review_status"] == "draft"
            and original["human_review_status"] == "pending",
            "draft status changed",
        )
    require(
        draft["artifact_bindings"]
        == {PATHS[k]: v for k, v in bindings.items() if k != "draft"},
        "stale draft bindings",
    )
    require(
        queries["artifact_bindings"][PATHS["evidence"]] == bindings["evidence"],
        "stale evidence binding",
    )
    public = queries_from_public(project_queries(queries))
    dev_public = queries_from_public(project_queries(dev))
    ids = tuple(q.query_id for q in public)
    require(len(ids) == 16 and len(dev_public) == 8, "expected 16/8 questions")
    require(not set(ids) & {q.query_id for q in dev_public}, "split query overlap")

    def families(x: dict[str, Any]) -> set[str]:
        return {q["curation"]["change_family"] for q in x["queries"]}

    require(not families(queries) & families(dev), "change_family leakage")
    require(tuple(draft["query_ids"]) == ids, "draft query IDs changed")
    units = tuple(evidence_record(u["record"]) for u in data["evidence"]["units"])
    known = {u.evidence_id: u for u in units}
    require(len(units) == len(known) == 34, "expected 34 unique units")
    sources = tuple(decode_record(s["record"]) for s in data["manifest"]["sources"])
    registry = {s.source_id: s for s in sources}
    require(len(registry) == len(sources), "duplicate source IDs")
    for u in units:
        require(digest(u.content.encode()) == u.content_hash, "content hash mismatch")
        for sid in {u.source_id} | {c.source_id for c in u.contributions}:
            require(
                sid in registry and registry[sid].ecosystem_id == u.ecosystem_id,
                "source/evidence mismatch",
            )
    require(
        data["evidence"]["selection_hash"] == data["manifest"]["selection_hash"],
        "selection mismatch",
    )
    judgments = tuple(judgment_record(r["judgment"]) for r in draft["judgments"])
    pairs = {(j.query_id, j.evidence_id) for j in judgments}
    require(
        len(judgments) == len(pairs) == 544
        and pairs == {(q, e) for q in ids for e in known},
        "incomplete/duplicate matrix",
    )
    issues = {}
    for row, j in zip(draft["judgments"], judgments, strict=True):
        require(
            j.review_status is ReviewStatus.DRAFT
            and row["human_review_status"] == "pending",
            "proposal status changed",
        )
        locators(j.supporting_locators, known[j.evidence_id])
        require(isinstance(row["unresolved_issues"], list), "issues must be a list")
        issues[j.query_id, j.evidence_id] = row["unresolved_issues"]
    proposals = draft["question_proposals"]
    require(
        len(proposals) == 16 and {q["query_id"] for q in proposals} == set(ids),
        "question proposals incomplete",
    )
    for q in proposals:
        require(q["human_review_status"] == "pending", "question review pending")
        positive = any(
            j.query_id == q["query_id"]
            and j.topical_relevance == 2
            and j.version_applicability.value == "valid"
            for j in judgments
        )
        require(
            positive
            == (Answerability(q["proposed_answerability"]) is Answerability.ANSWERABLE),
            "answerability/positive mismatch",
        )
        # Any original question-level concern remains blocking, not silently discarded.
        require(
            isinstance(q["unresolved_issues"], list), "question issues must be a list"
        )
    curation = {
        q["retriever_input"]["query_id"]: q["curation"] for q in queries["queries"]
    }
    for row in curation.values():
        QueryCategory(row["primary_category"])
    return Pilot(
        bindings,
        sources,
        units,
        public,
        curation,
        judgments,
        issues,
        "heldout-gold-only",
    ), draft


def readiness(root: Path, *, evaluation: bool = False) -> dict[str, Any]:
    pilot, draft = load_heldout(root, evaluation=evaluation)
    decisions = decode_json((root / DECISIONS).read_bytes())
    report = review(pilot, decisions, heldout=True)[0]
    original_question_issues = [
        f"{q['query_id']}: {issue}"
        for q in draft["question_proposals"]
        for issue in q["unresolved_issues"]
    ]
    report["unresolved_issues"].extend(original_question_issues)
    report["gold_ready"] = report["scoring_permitted"] and not original_question_issues
    report["scoring_permitted"] = report["gold_ready"] and evaluation
    report["scope"] = "explicit review gate; readiness never reads rankings"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--evaluation", action="store_true", help="M2.6b approved evaluation scope"
    )
    args = parser.parse_args()
    print(
        json.dumps(
            readiness(args.root, evaluation=args.evaluation),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
