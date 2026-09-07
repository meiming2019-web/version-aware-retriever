"""Fixed rank-only RRF over frozen runs; no gold, evaluator, or model execution."""

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import RankedResult
from version_aware_retriever.lexical import (
    SearchHit,
    canonical,
    documents_from_artifact,
    queries_from_public,
)

RRF_K = 60
CONFIG = {
    "algorithm": "reciprocal-rank-fusion-v1",
    "rrf_k": RRF_K,
    "weights": {"bm25": 1.0, "dense": 1.0},
    "rank_base": 1,
    "missing_contribution": 0,
    "return_policy": (
        "full union; descending unrounded RRF; exact ties ascending evidence_id"
    ),
}
EVIDENCE = "data/pydantic/extraction/derived/evidence.json"
QUERIES = "data/pydantic/benchmark/queries.dev.input.json"
OUTPUT = "data/pydantic/runs/rrf-hybrid.dev.unscored.json"


@dataclass(frozen=True)
class SourcePin:
    method: str
    path: str
    run_id: str
    content_hash: str


SOURCES = (
    SourcePin(
        "bm25",
        "data/pydantic/runs/bm25.dev.unscored.json",
        "bm25:1a06c16b2d1e48343635db4ddb27a0a09a7e78aa8e552561e915ae599588af03",
        "sha256:bd1965bf01def986a9abbb72198316ca042f66f9a53e23310c25a11d9dea01fc",
    ),
    SourcePin(
        "dense",
        "data/pydantic/runs/dense.dev.unscored.json",
        "dense:35c5c526dacd51c77850519d7a14bc23c2f46c7dd7c6728baddaccb95d4bed2e",
        "sha256:e06428ec27f4f5438205e43ef1d2b46cec4f007de8cae51226d2c590b697066c",
    ),
)


def fuse(bm25: tuple[str, ...], dense: tuple[str, ...]) -> tuple[SearchHit, ...]:
    """Two positional rankings only. Missing items receive zero contribution."""
    for ranking in (bm25, dense):
        RankedResult(query_id="rrf-input", evidence_ids=ranking)
        require(
            all(not any(c.isspace() for c in eid) for eid in ranking),
            "invalid evidence ID",
        )
    b = {eid: rank for rank, eid in enumerate(bm25, 1)}
    d = {eid: rank for rank, eid in enumerate(dense, 1)}
    hits = []
    for eid in b.keys() | d.keys():
        value = math.fsum(
            (
                1 / (RRF_K + b[eid]) if eid in b else 0.0,
                1 / (RRF_K + d[eid]) if eid in d else 0.0,
            )
        )
        require(math.isfinite(value), "nonfinite RRF score")
        hits.append(SearchHit(eid, value))
    return tuple(sorted(hits, key=lambda h: (-h.score, h.evidence_id)))


def decode(body: bytes) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    return json.loads(body, object_pairs_hook=unique)


def source_rankings(
    body: bytes,
    pin: SourcePin,
    snapshot: str,
    hashes: dict[str, str],
    query_ids: set[str],
    evidence_ids: set[str],
) -> dict[str, tuple[str, ...]]:
    """Check frozen bytes and public input compatibility before exposing ranks."""
    require(digest(body) == pin.content_hash, "frozen source-run hash mismatch")
    data = decode(body)
    require(data["run_id"] == pin.run_id, "source-run identity mismatch")
    require(
        data["format_version"] == 1 and data["status"] == "unscored",
        "unexpected run format/status",
    )
    require(
        data["retrieval_input_snapshot"] == snapshot, "incompatible source snapshot"
    )
    require(data["artifact_hashes"] == hashes, "incompatible source artifact hashes")
    depth = data["run_depth"]
    require(
        type(depth) is int and 0 <= depth <= len(evidence_ids), "invalid source depth"
    )
    rows = tuple(
        RankedResult(query_id=r["query_id"], evidence_ids=tuple(r["evidence_ids"]))
        for r in data["results"]
    )
    require(
        len(rows) == len(query_ids) and {r.query_id for r in rows} == query_ids,
        "missing, duplicate or unknown source query IDs",
    )
    for row in rows:
        require(set(row.evidence_ids) <= evidence_ids, "unknown source evidence IDs")
        require(len(row.evidence_ids) <= depth, "source ranking exceeds declared depth")
    diagnostics = data["diagnostics"]
    require(
        len(diagnostics) == len(query_ids)
        and {r["query_id"] for r in diagnostics} == query_ids,
        "missing or duplicate source diagnostics",
    )
    scores = {row["query_id"]: row["scores"] for row in diagnostics}
    for row in rows:
        values = scores[row.query_id]
        require(
            len(values) == len(row.evidence_ids)
            and all(type(x) in (float, int) and math.isfinite(x) for x in values),
            "invalid source score alignment",
        )
    # Source score values are checked for integrity, never passed to fusion.
    return {row.query_id: row.evidence_ids for row in rows}


def run_development(
    root: Path,
    *,
    sources: tuple[SourcePin, ...] = SOURCES,
    public_queries: str = QUERIES,
    output_path: str = OUTPUT,
    expected_queries: int = 8,
) -> dict[str, Any]:
    """Read exactly four input files; output is read only for no-op rewrite checks."""
    require(
        tuple(s.method for s in sources) == ("bm25", "dense"),
        "expected two fixed methods",
    )
    paths = [root / EVIDENCE, root / public_queries, *(root / s.path for s in sources)]
    output = root / output_path
    require(len({p.resolve() for p in (*paths, output)}) == 5, "overlapping paths")
    evidence_bytes, query_bytes, bm25_bytes, dense_bytes = [
        p.read_bytes() for p in paths
    ]
    documents = tuple(
        sorted(
            documents_from_artifact(decode(evidence_bytes)), key=lambda d: d.evidence_id
        )
    )
    queries = queries_from_public(decode(query_bytes))
    known = {d.evidence_id for d in documents}
    require(
        len(documents) == len(known) == 34 and len(queries) == expected_queries,
        f"expected 34 unique documents and {expected_queries} public queries",
    )
    require(
        all(q.ecosystem_id in {d.ecosystem_id for d in documents} for q in queries),
        "query ecosystem absent",
    )
    snapshot = (
        "retrieval-input:"
        + digest(
            canonical(
                {
                    "documents": [asdict(d) for d in documents],
                    "queries": [asdict(q) for q in queries],
                }
            )
        )[7:]
    )
    hashes = {"evidence": digest(evidence_bytes), "public_queries": digest(query_bytes)}
    source_rows = [
        source_rankings(
            body, pin, snapshot, hashes, {q.query_id for q in queries}, known
        )
        for body, pin in zip((bm25_bytes, dense_bytes), sources, strict=True)
    ]
    results, diagnostics = [], []
    for query in queries:
        hits = fuse(source_rows[0][query.query_id], source_rows[1][query.query_id])
        results.append(
            asdict(
                RankedResult(
                    query_id=query.query_id,
                    evidence_ids=tuple(h.evidence_id for h in hits),
                )
            )
        )
        diagnostics.append(
            {"query_id": query.query_id, "scores": [h.score for h in hits]}
        )
    provenance = [
        {"method": pin.method, "run_id": pin.run_id, "content_hash": digest(body)}
        for pin, body in zip(sources, (bm25_bytes, dense_bytes), strict=True)
    ]
    report = {
        "format_version": 1,
        "status": "unscored",
        "run_id": "rrf-hybrid:"
        + digest(
            canonical(
                {
                    "sources": provenance,
                    "configuration": CONFIG,
                    "retrieval_input_snapshot": snapshot,
                }
            )
        )[7:],
        "source_runs": provenance,
        "retrieval_input_snapshot": snapshot,
        "artifact_hashes": hashes,
        "configuration": CONFIG,
        "run_depth": len(documents),
        "results": results,
        "diagnostics": diagnostics,
    }
    encoded = (
        json.dumps(
            report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode()
    require(
        not any(p.is_symlink() for p in (output, *output.parents)), "output symlink"
    )
    if not output.exists() or output.read_bytes() != encoded:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encoded)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    report = run_development(args.root)
    print(f"{report['run_id']}: eight development queries, unscored")


if __name__ == "__main__":
    main()
