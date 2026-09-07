"""Explicit approved benchmark/projection and post-freeze scoring; no inference."""

import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import Benchmark, RankedRun
from version_aware_retriever.evaluation import CUTOFFS, evaluate
from version_aware_retriever.heldout_retrieval import PUBLIC, validate
from version_aware_retriever.heldout_review import DECISIONS, load_heldout, readiness
from version_aware_retriever.lexical import canonical, project_queries
from version_aware_retriever.pilot_evaluation import (
    decode_json,
    review,
    save_result,
    saved_results,
)

OUTPUT = "data/pydantic/results/heldout.four-methods.json"


def benchmark(root: Path) -> Benchmark:
    require(
        readiness(root, evaluation=True)["scoring_permitted"],
        "held-out review incomplete",
    )
    pilot, _ = load_heldout(root, evaluation=True)
    decisions = decode_json((root / DECISIONS).read_bytes())
    _, questions, judgments = review(pilot, decisions, heldout=True)
    revision = (
        "heldout:"
        + digest(canonical({"bindings": pilot.bindings, "decisions": decisions}))[7:]
    )
    return Benchmark(
        benchmark_revision=revision,
        sources=pilot.sources,
        evidence=pilot.evidence,
        queries=questions,
        judgments=judgments,
    )


def project(root: Path) -> str:
    approved = benchmark(root)
    draft = decode_json(
        (root / "data/pydantic/benchmark/queries.eval.draft.json").read_bytes()
    )
    public = project_queries(draft)
    require(
        {q["query_id"] for q in public} == {q.query_id for q in approved.queries},
        "projection ID mismatch",
    )
    body = (
        json.dumps(public, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()
    save_result(root / PUBLIC, body)
    return approved.benchmark_revision


def score(root: Path) -> bytes:
    # All four runs must exist and pass source/input/candidate checks before gold.
    bodies = validate(root)
    approved = benchmark(root)
    pilot, _ = load_heldout(root, evaluation=True)
    public = decode_json((root / PUBLIC).read_bytes())
    draft = decode_json(
        (root / "data/pydantic/benchmark/queries.eval.draft.json").read_bytes()
    )
    require(
        public == project_queries(draft),
        "public projection differs from reviewed queries",
    )
    pilot = replace(
        pilot,
        bindings={
            **pilot.bindings,
            "public_queries": digest((root / PUBLIC).read_bytes()),
        },
        snapshot=decode_json(bodies[0])["retrieval_input_snapshot"],
    )
    rows = []
    for method, body in zip(
        ("bm25", "dense", "rrf", "cross-encoder"), bodies, strict=True
    ):
        data = decode_json(body)
        run = RankedRun(
            run_id="heldout-run:"
            + digest(
                canonical(
                    {"benchmark": approved.benchmark_revision, "run": digest(body)}
                )
            )[7:],
            benchmark_revision=approved.benchmark_revision,
            method_description=data["configuration"]["return_policy"],
            results=saved_results(pilot, body),
        )
        categories = {}
        for category in sorted({q.primary_category for q in approved.queries}):
            ids = {
                q.query_id for q in approved.queries if q.primary_category == category
            }
            subset = replace(
                approved,
                queries=tuple(q for q in approved.queries if q.query_id in ids),
                judgments=tuple(j for j in approved.judgments if j.query_id in ids),
            )
            categories[category.value] = asdict(
                evaluate(
                    subset,
                    replace(
                        run, results=tuple(r for r in run.results if r.query_id in ids)
                    ),
                )
            )
        rows.append(
            {
                "method": method,
                "original_run_id": data["run_id"],
                "original_run_hash": digest(body),
                "adapted_run": asdict(run),
                "evaluation": asdict(evaluate(approved, run)),
                "categories": categories,
            }
        )
    report = {
        "format": "heldout-four-methods-v1",
        "benchmark_revision": approved.benchmark_revision,
        "bindings": {
            **pilot.bindings,
            "review_decisions": digest((root / DECISIONS).read_bytes()),
            "public_queries": digest((root / PUBLIC).read_bytes()),
        },
        "reviewed_queries": [asdict(q) for q in approved.queries],
        "reviewed_judgments": [asdict(j) for j in approved.judgments],
        "evaluator": {
            "cutoffs": CUTOFFS,
            "source_hash": digest(
                Path(__file__).with_name("evaluation.py").read_bytes()
            ),
            "contracts_hash": digest(
                Path(__file__).with_name("contracts.py").read_bytes()
            ),
        },
        "runs": rows,
    }
    report["result_id"] = "heldout-result:" + digest(canonical(report))[7:]
    return (
        json.dumps(
            report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("project", "score"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.command == "project":
        print(project(args.root))
    else:
        body = score(args.root)
        save_result(args.root / OUTPUT, body)
        print(body.decode(), end="")


if __name__ == "__main__":
    main()
