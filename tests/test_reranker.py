"""Fictional fixtures and mock scores only; never load a model or real gold."""

import copy
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.acquisition import digest
from version_aware_retriever.hybrid import SourcePin
from version_aware_retriever.lexical import (
    canonical,
    documents_from_artifact,
    queries_from_public,
)
from version_aware_retriever.reranker import (
    EVIDENCE,
    MANIFEST,
    OUTPUT,
    QUERIES,
    SOURCE,
    passage,
    rerank,
    run_development,
    top20,
)


def test_order_ties_and_immutability() -> None:
    ids = ("z", "a", "b")
    scores = [1.0, 1.0, 2.0]
    assert rerank("q:fiction", ids, scores) == ("b", "z", "a")
    assert ids == ("z", "a", "b") and scores == [1, 1, 2]


@pytest.mark.parametrize(
    "ids,scores",
    [
        ((), []),
        (("a", "a"), [1, 2]),
        (("bad id",), [1]),
        (("",), [1]),
        (("a",), []),
        (("a",), [float("nan")]),
        (("a",), [float("inf")]),
        (("a",), [float("-inf")]),
    ],
)
def test_reject_bad_rankings(ids: tuple[str, ...], scores: list[float]) -> None:
    with pytest.raises(ValueError):
        rerank("q:fiction", ids, scores)


def test_top20() -> None:
    ids = tuple(f"e:{i}" for i in range(34))
    assert top20(ids, set(ids)) == ids[:20]
    for bad, known in [
        (ids, set(ids[:20])),
        (ids[:19], set(ids)),
        (ids + (ids[0],), set(ids)),
    ]:
        with pytest.raises(ValueError):
            top20(bad, known)


def test_passage_allowlist() -> None:
    record = {"source_id": "s", "ecosystem_id": "fiction", "content": "Verbatim\n"}
    source = {
        "ecosystem_id": "fiction",
        "document_type": "migration_guide",
        "document_version": {"kind": "exact", "value": "r2"},
    }
    expected = (
        "[Document snapshot: fiction r2]\n"
        "[Document type: migration_guide]\n\nVerbatim\n"
    )
    assert passage(record, {"s": source}) == expected
    for name in (
        "applicability",
        "gold",
        "review_status",
        "key",
        "evidence_roles",
        "hard_negative",
    ):
        assert (
            passage(
                {**record, name: "do not use"}, {"s": {**source, name: "do not use"}}
            )
            == expected
        )
    with pytest.raises(ValueError):
        passage(record, {})
    with pytest.raises(ValueError):
        passage(record, {"s": {**source, "ecosystem_id": "other"}})


class MockScorer:
    def __init__(self, oversized: bool = False) -> None:
        self.oversized = oversized
        self.scored = False

    def lengths(self, pairs: list[tuple[str, str]]) -> list[int]:
        assert len(pairs) == 160
        assert all("Document snapshot" in p for _, p in pairs)
        return [8193 if self.oversized else 42] * len(pairs)

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        self.scored = True
        return [float(i % 20) for i in range(len(pairs))]


def fixture(root: Path) -> SourcePin:
    records = [
        {
            "evidence_id": f"e:{i:02}",
            "ecosystem_id": "fiction",
            "source_id": "s",
            "content": f"Fictional passage {i}",
        }
        for i in range(34)
    ]
    artifact = {"units": [{"record": r} for r in records]}
    queries = [
        {
            "query_id": f"q:{i}",
            "ecosystem_id": "fiction",
            "query_text": "Fictional question?",
            "query_kind": "lookup",
            "source_version": None,
            "requested_version": {"kind": "exact", "scheme": "fiction", "value": "r2"},
        }
        for i in range(8)
    ]
    manifest = {
        "sources": [
            {
                "record": {
                    "source_id": "s",
                    "ecosystem_id": "fiction",
                    "document_version": {"kind": "exact", "value": "r2"},
                    "document_type": "conceptual_guide",
                }
            }
        ]
    }
    hashes = {
        "evidence": digest(canonical(artifact)),
        "public_queries": digest(canonical(queries)),
    }
    snapshot = (
        "retrieval-input:"
        + digest(
            canonical(
                {
                    "documents": [asdict(d) for d in documents_from_artifact(artifact)],
                    "queries": [asdict(q) for q in queries_from_public(queries)],
                }
            )
        )[7:]
    )
    run = {
        "format_version": 1,
        "status": "unscored",
        "run_id": "fiction:rrf",
        "retrieval_input_snapshot": snapshot,
        "artifact_hashes": hashes,
        "run_depth": 34,
        "results": [
            {
                "query_id": q["query_id"],
                "evidence_ids": [r["evidence_id"] for r in records],
            }
            for q in queries
        ],
        "diagnostics": [
            {"query_id": q["query_id"], "scores": [1.0] * 34} for q in queries
        ],
    }
    for name, data in [
        (EVIDENCE, artifact),
        (QUERIES, queries),
        (MANIFEST, manifest),
        (SOURCE.path, run),
    ]:
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(canonical(data))
    return SourcePin("rrf", SOURCE.path, "fiction:rrf", digest(canonical(run)))


def test_guarded_generation_and_length_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = fixture(tmp_path)
    allowed = {tmp_path / p for p in (EVIDENCE, QUERIES, MANIFEST, SOURCE.path, OUTPUT)}
    read = Path.read_bytes
    before = {p: read(p) for p in allowed if p.exists()}

    def guarded(p: Path) -> bytes:
        assert p in allowed, f"Forbidden input: {p}"
        return read(p)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    blocked = MockScorer(True)
    with pytest.raises(ValueError, match="input length blocker"):
        run_development(tmp_path, blocked, {"test_only": True}, source=source)
    assert not blocked.scored and not (tmp_path / OUTPUT).exists()
    result = run_development(tmp_path, MockScorer(), {"test_only": True}, source=source)
    output = tmp_path / OUTPUT
    saved = output.read_bytes(), output.stat().st_mtime_ns
    assert result == run_development(
        tmp_path, MockScorer(), {"test_only": True}, source=source
    )
    assert saved == (output.read_bytes(), output.stat().st_mtime_ns)
    for row in result["results"]:
        assert row["evidence_ids"] == tuple(f"e:{i:02}" for i in reversed(range(20)))
    assert before == {p: read(p) for p in before}
    original: Any = json.loads(read(tmp_path / EVIDENCE))
    changed = copy.deepcopy(original)
    for u in changed["units"]:
        u["record"]["applicability"] = ["ignored"]
    # Input hashes bind revisions, but constructed passages must not use annotations.
    sources = {"s": json.loads(read(tmp_path / MANIFEST))["sources"][0]["record"]}
    assert [passage(u["record"], sources) for u in original["units"]] == [
        passage(u["record"], sources) for u in changed["units"]
    ]
