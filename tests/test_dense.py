"""Synthetic only: no model download or real annotation access."""

import json
import math
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from version_aware_retriever.dense import (
    Vector,
    VectorIndex,
    embedding_pass,
    load_cache,
    normalize,
    run_development,
    snapshot,
)


def test_hand_calculation() -> None:
    index = VectorIndex(
        ("D1", "D2", "D3", "D4"), ((1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (-1.0, 0.0))
    )
    hits = index.search((1.0, 0.0))
    assert [h.evidence_id for h in hits] == ["D1", "D2", "D3", "D4"]
    assert [h.score for h in hits] == pytest.approx([1, 1 / math.sqrt(2), 0, -1])
    assert index.search((1.0, 0.0)) == hits
    assert index.search((1.0, 0.0), 2) == hits[:2]
    assert index.search((1.0, 0.0), 0) == ()


@pytest.mark.parametrize("vector", [(), (0.0, 0.0), (math.nan,), (math.inf,)])
def test_invalid_vectors(vector: Vector) -> None:
    with pytest.raises(ValueError):
        normalize(vector)


def test_alignment_dimensions_ties_and_empty() -> None:
    assert normalize((3.0, 4.0)) == (0.6, 0.8)
    with pytest.raises(ValueError):
        VectorIndex(("a",), ())
    with pytest.raises(ValueError):
        VectorIndex(("a", "a"), ((1.0,), (1.0,)))
    with pytest.raises(ValueError):
        VectorIndex(("a", "b"), ((1.0,), (1.0, 2.0)))
    index = VectorIndex(("b", "a"), ((1.0, 0.0), (0.0, 1.0)))
    assert index.search((0.0, 1.0))[0].evidence_id == "a"
    assert [h.evidence_id for h in index.search((1.0, 1.0))] == ["a", "b"]
    with pytest.raises(ValueError):
        index.search((1.0,))
    assert VectorIndex((), ()).search((1.0,)) == ()


@pytest.mark.parametrize("k", [-1, True, 1.5])
def test_invalid_k(k: Any) -> None:
    with pytest.raises(ValueError):
        VectorIndex((), ()).search((1.0,), k)


class MockEncoder:
    def __init__(self, length: int = 10) -> None:
        self.length = length
        self.seen: list[str] = []

    def lengths(self, texts: list[str]) -> list[int]:
        return [self.length] * len(texts)

    def encode(self, texts: list[str]) -> tuple[Vector, ...]:
        self.seen.extend(texts)
        return tuple((1.0, float(len(t))) for t in texts)


def test_limit_before_encode() -> None:
    encoder = MockEncoder(8193)
    with pytest.raises(ValueError, match="doc: token length 8193"):
        embedding_pass(encoder, ("doc",), ["text"])
    assert encoder.seen == []
    assert embedding_pass(encoder, (), []) == ((), [])
    assert embedding_pass(MockEncoder(8192), ("doc",), ["text"])[1] == [8192]


def test_missing_model_is_local_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, Any]] = []

    def missing(*args: Any, **kwargs: Any) -> str:
        calls.append(kwargs)
        raise OSError("synthetic missing snapshot")

    monkeypatch.setattr(
        "version_aware_retriever.dense.importlib.import_module",
        lambda name: SimpleNamespace(snapshot_download=missing),
    )
    with pytest.raises(ValueError, match="prepare"):
        snapshot()
    assert calls[0]["local_files_only"] is True
    assert len(calls[0]["revision"]) == 40
    assert "model.safetensors" in calls[0]["allow_patterns"]
    assert not any(x.endswith(".bin") for x in calls[0]["allow_patterns"])


def test_runner_isolation_cache_and_reproducibility(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence, queries, output, cache = [tmp_path / n for n in ("e", "q", "o", "c")]
    units = [
        {
            "record": {
                "evidence_id": f"d:{i:02}",
                "ecosystem_id": "test",
                "content": f"Content {i}",
                "applicability": "DO NOT ENCODE",
            }
        }
        for i in range(34)
    ]
    evidence.write_text(json.dumps({"units": units}))
    queries.write_text(
        json.dumps(
            [
                {
                    "query_id": f"q:{i}",
                    "ecosystem_id": "test",
                    "query_text": f"Question {i}",
                    "query_kind": "lookup",
                    "source_version": None,
                    "requested_version": {
                        "kind": "exact",
                        "scheme": "test",
                        "value": "1",
                    },
                }
                for i in range(8)
            ]
        )
    )
    original = Path.read_bytes
    reads: list[Path] = []

    def guarded(path: Path) -> bytes:
        assert path in (evidence, queries, output, cache)
        reads.append(path)
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    encoder = MockEncoder()
    first = run_development(evidence, queries, output, cache, encoder=encoder)
    assert len(encoder.seen) == 42
    assert encoder.seen == [f"Content {i}" for i in range(34)] + [
        f"Question {i}" for i in range(8)
    ]
    assert all(len(r["evidence_ids"]) == 34 for r in first["results"])
    before = (
        output.read_bytes(),
        output.stat().st_mtime_ns,
        cache.read_bytes(),
        cache.stat().st_mtime_ns,
    )
    second = run_development(evidence, queries, output, cache)
    assert first == second
    assert before == (
        output.read_bytes(),
        output.stat().st_mtime_ns,
        cache.read_bytes(),
        cache.stat().st_mtime_ns,
    )
    fresh = run_development(
        evidence, queries, output, cache, fresh=True, encoder=MockEncoder()
    )
    assert fresh == first
    units[0]["record"]["applicability"] = "changed outside projection"
    evidence.write_text(json.dumps({"units": units}))
    changed = run_development(evidence, queries, output, cache)
    assert changed["results"] == first["results"]
    assert changed["run_id"] == first["run_id"]
    artifact = json.loads(cache.read_bytes())
    binding = artifact["binding"]
    with pytest.raises(ValueError, match="stale"):
        load_cache(cache, {**binding, "ids": list(reversed(binding["ids"]))})
    artifact["vectors"][0][0] += 1
    cache.write_text(json.dumps(artifact))
    with pytest.raises(ValueError, match="hash"):
        load_cache(cache, binding)
    assert set(reads) <= {evidence, queries, output, cache}
