"""Fixed batch reuse, input isolation and post-freeze scoring checks."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from version_aware_retriever import hybrid, reranker
from version_aware_retriever.contracts import RankedResult, RankedRun
from version_aware_retriever.evaluation import evaluate
from version_aware_retriever.heldout_evaluation import benchmark, project, score
from version_aware_retriever.heldout_retrieval import PUBLIC, RUNS, run, validate
from version_aware_retriever.heldout_review import DECISIONS, PATHS, readiness


class FictionalEncoder:
    def lengths(self, texts: list[str]) -> list[int]:
        return [10] * len(texts)

    def encode(self, texts: list[str]) -> tuple[tuple[float, ...], ...]:
        return tuple((1.0, float(i + 1)) for i in range(len(texts)))


class FictionalScorer:
    def lengths(self, pairs: list[tuple[str, str]]) -> list[int]:
        assert len(pairs) == 320
        return [20] * len(pairs)

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        return [float(i % 20) for i in range(len(pairs))]


def test_generation_without_gold_and_frozen_candidates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = {
        "units": [
            {
                "record": {
                    "evidence_id": f"e:{i:02}",
                    "ecosystem_id": "fiction",
                    "content": f"Fictional passage {i}",
                    "source_id": "s",
                }
            }
            for i in range(34)
        ]
    }
    queries = [
        {
            "query_id": f"q:fictional-{i}",
            "ecosystem_id": "fiction",
            "query_text": "Fictional passage",
            "query_kind": "lookup",
            "source_version": None,
            "requested_version": {"kind": "exact", "scheme": "fiction", "value": "r2"},
        }
        for i in range(16)
    ]
    manifest = {
        "sources": [
            {
                "record": {
                    "source_id": "s",
                    "ecosystem_id": "fiction",
                    "document_type": "conceptual_guide",
                    "document_version": {"kind": "exact", "value": "r2"},
                }
            }
        ]
    }
    for name, data in (
        (hybrid.EVIDENCE, artifact),
        (PUBLIC, queries),
        (reranker.MANIFEST, manifest),
    ):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data))
    allowed = {
        tmp_path / p
        for p in (
            hybrid.EVIDENCE,
            PUBLIC,
            reranker.MANIFEST,
            *RUNS,
            ".dense-cache/heldout-embeddings.json",
        )
    }
    read_bytes, read_text = Path.read_bytes, Path.read_text

    def guarded_bytes(p: Path) -> bytes:
        assert p in allowed, f"Forbidden gold/review/result read: {p}"
        return read_bytes(p)

    def guarded_text(p: Path, *args: object, **kwargs: object) -> str:
        assert p in allowed, f"Forbidden gold/review/result read: {p}"
        return read_text(p)

    monkeypatch.setattr(Path, "read_bytes", guarded_bytes)
    monkeypatch.setattr(Path, "read_text", guarded_text)
    monkeypatch.setattr("importlib.metadata.version", lambda name: "synthetic-test")
    run(
        tmp_path,
        encoder=FictionalEncoder(),
        scorer=FictionalScorer(),
        runtime={"test_only": True},
    )
    bodies = validate(tmp_path)
    assert len(bodies) == 4
    reports = [json.loads(b) for b in bodies]
    assert all(len(d["results"]) == 16 for d in reports)
    assert reports[1]["vector_shapes"] == [[34, 2], [16, 2]]
    assert all(len(r["evidence_ids"]) == 20 for r in reports[3]["results"])
    with pytest.raises(ValueError, match="already exist"):
        run(tmp_path, encoder=FictionalEncoder(), scorer=FictionalScorer(), runtime={})
    assert bodies == validate(tmp_path)
    # Frozen configuration checks reject changes without interpreting rankings.
    bad = reports[2]
    bad["configuration"]["rrf_k"] = 61
    (tmp_path / RUNS[2]).write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="configuration"):
        validate(tmp_path)


def test_real_approved_projection_and_gate(tmp_path: Path) -> None:
    original = Path(__file__).resolve().parents[1]
    for name in (*PATHS.values(), DECISIONS):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((original / name).read_bytes())
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    r = readiness(tmp_path, evaluation=True)
    assert r["question_decisions"]["reviewed"] == 16
    assert r["pair_decisions"]["reviewed"] == 544 and r["scoring_permitted"]
    b = benchmark(tmp_path)
    assert len(b.queries) == 16 and len(b.judgments) == 544
    assert sum(j.is_valid_positive for j in b.judgments) == 28
    assert sum(j.hard_negative for j in b.judgments) == 1
    revision = project(tmp_path)
    p = tmp_path / PUBLIC
    saved = p.read_bytes(), p.stat().st_mtime_ns
    assert project(tmp_path) == revision == b.benchmark_revision
    assert saved == (p.read_bytes(), p.stat().st_mtime_ns)
    assert before == {p: p.read_bytes() for p in before}
    with pytest.raises(FileNotFoundError):
        score(tmp_path)  # No scoring without all four frozen runs.


def test_frozen_real_scoring_is_deterministic_and_uses_existing_evaluator() -> None:
    root = Path(__file__).resolve().parents[1]
    protected = [root / p for p in (*PATHS.values(), DECISIONS, PUBLIC, *RUNS)]
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in protected}
    first = score(root)
    assert first == score(root)
    report = json.loads(first)
    approved = benchmark(root)
    assert report["benchmark_revision"] == approved.benchmark_revision
    for row in report["runs"]:
        data = row["adapted_run"]
        run_record = RankedRun(
            **{
                **data,
                "results": tuple(
                    RankedResult(
                        query_id=r["query_id"], evidence_ids=tuple(r["evidence_ids"])
                    )
                    for r in data["results"]
                ),
            }
        )
        assert row["evaluation"] == json.loads(
            json.dumps(asdict(evaluate(approved, run_record)))
        )
        assert sum(c["query_count"] for c in row["categories"].values()) == 16
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in protected}
