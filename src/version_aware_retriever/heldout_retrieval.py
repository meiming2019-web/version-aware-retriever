"""One frozen four-method held-out batch; only public/content/source inputs."""

import argparse
import time
from pathlib import Path
from typing import Any

from version_aware_retriever import dense, hybrid, lexical, reranker
from version_aware_retriever.acquisition import digest, require

PUBLIC = "data/pydantic/benchmark/queries.eval.input.json"
RUNS = (
    "data/pydantic/runs/bm25.eval.unscored.json",
    "data/pydantic/runs/dense.eval.unscored.json",
    "data/pydantic/runs/rrf-hybrid.eval.unscored.json",
    "data/pydantic/runs/cross-encoder-reranked.eval.unscored.json",
)


def pin(root: Path, index: int, method: str) -> hybrid.SourcePin:
    body = (root / RUNS[index]).read_bytes()
    return hybrid.SourcePin(
        method, RUNS[index], hybrid.decode(body)["run_id"], digest(body)
    )


def validate(root: Path) -> tuple[bytes, ...]:
    """Check all four frozen outputs without loading judgments/review/results."""
    eb, qb = (root / hybrid.EVIDENCE).read_bytes(), (root / PUBLIC).read_bytes()
    docs = lexical.documents_from_artifact(hybrid.decode(eb))
    queries = lexical.queries_from_public(hybrid.decode(qb))
    require(len(docs) == 34 and len(queries) == 16, "unexpected held-out inventory")
    from dataclasses import asdict

    snapshot = (
        "retrieval-input:"
        + digest(
            lexical.canonical(
                {
                    "documents": [
                        asdict(d) for d in sorted(docs, key=lambda d: d.evidence_id)
                    ],
                    "queries": [asdict(q) for q in queries],
                }
            )
        )[7:]
    )
    hashes = {"evidence": digest(eb), "public_queries": digest(qb)}
    bodies = tuple((root / name).read_bytes() for name in RUNS)
    data = [hybrid.decode(b) for b in bodies]
    rows = []
    for i, (body, config) in enumerate(
        zip(
            bodies,
            (lexical.CONFIG, dense.CONFIG, hybrid.CONFIG, reranker.CONFIG),
            strict=True,
        )
    ):
        r = data[i]
        require(r["configuration"] == config, "frozen configuration mismatch")
        row = hybrid.source_rankings(
            body,
            hybrid.SourcePin("heldout", RUNS[i], r["run_id"], digest(body)),
            snapshot,
            hashes,
            {q.query_id for q in queries},
            {d.evidence_id for d in docs},
        )
        require(r["run_depth"] == (20 if i == 3 else 34), "declared depth mismatch")
        if i in (1, 2):
            require(
                all(len(ids) == 34 for ids in row.values()),
                "full-corpus return required",
            )
        rows.append(row)
    require(
        all(s > 0 for row in data[0]["diagnostics"] for s in row["scores"]),
        "BM25 return policy changed",
    )
    require(
        data[2]["source_runs"]
        == [
            {
                "method": m,
                "run_id": data[i]["run_id"],
                "content_hash": digest(bodies[i]),
            }
            for i, m in enumerate(("bm25", "dense"))
        ],
        "RRF source lineage mismatch",
    )
    require(
        data[3]["source_rrf"]
        == {"run_id": data[2]["run_id"], "content_hash": digest(bodies[2])},
        "cross-encoder source lineage mismatch",
    )
    for q in queries:
        require(
            len(rows[3][q.query_id]) == 20
            and set(rows[3][q.query_id]) == set(rows[2][q.query_id][:20]),
            "cross-encoder candidate set changed",
        )
    require(
        data[3]["manifest_hash"] == digest((root / reranker.MANIFEST).read_bytes()),
        "manifest binding mismatch",
    )
    require(
        data[3]["input_lengths"]["maximum"] <= 8192
        and data[3]["input_lengths"]["truncation_count"] == 0,
        "cross-encoder truncation",
    )
    require(data[1]["length_checks"]["truncations"] == 0, "dense truncation")
    return bodies


def run(
    root: Path,
    *,
    encoder: dense.Encoder | None = None,
    scorer: reranker.PairScorer | None = None,
    runtime: dict[str, Any] | None = None,
) -> None:
    # No gold-based branching or review imports. The separate approval/projection
    # step authorizes this invocation before its retrieval-only process starts.
    require(
        not any((root / p).exists() for p in RUNS),
        "held-out outputs already exist; refuse a new experiment",
    )
    lexical.run_development(
        root / hybrid.EVIDENCE, root / PUBLIC, root / RUNS[0], expected_queries=16
    )
    print("BM25 frozen", flush=True)
    start = time.perf_counter()
    dense.run_development(
        root / hybrid.EVIDENCE,
        root / PUBLIC,
        root / RUNS[1],
        root / ".dense-cache/heldout-embeddings.json",
        fresh=True,
        encoder=encoder,
        expected_queries=16,
    )
    print(f"Dense frozen; CPU elapsed {time.perf_counter() - start:.3f}s", flush=True)
    hybrid.run_development(
        root,
        sources=(pin(root, 0, "bm25"), pin(root, 1, "dense")),
        public_queries=PUBLIC,
        output_path=RUNS[2],
        expected_queries=16,
    )
    print("RRF frozen", flush=True)
    start = time.perf_counter()
    if scorer is None:
        local = reranker.LocalScorer()
        scorer, runtime = local, local.runtime
    require(runtime is not None, "scorer runtime required")
    assert runtime is not None
    reranker.run_development(
        root,
        scorer,
        runtime,
        source=pin(root, 2, "rrf-hybrid"),
        public_queries=PUBLIC,
        output_path=RUNS[3],
        expected_queries=16,
    )
    print(
        f"Cross-encoder frozen; CPU elapsed {time.perf_counter() - start:.3f}s",
        flush=True,
    )
    validate(root)
    print(
        "All four held-out runs frozen and structurally verified; no gold loaded",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    run(args.root)


if __name__ == "__main__":
    main()
