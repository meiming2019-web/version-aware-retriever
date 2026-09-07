"""Fictional rank lists only; no labels, model inference, or evaluator inputs."""

import json
import math
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.acquisition import digest
from version_aware_retriever.hybrid import (
    EVIDENCE,
    OUTPUT,
    QUERIES,
    SOURCES,
    SourcePin,
    fuse,
    run_development,
)
from version_aware_retriever.lexical import (
    canonical,
    documents_from_artifact,
    queries_from_public,
)


def test_hand_calculation() -> None:
    hits = fuse(("A", "B", "C"), ("C", "B", "D"))
    expected = {"A": 1 / 61, "B": 1 / 62 + 1 / 62, "C": 1 / 63 + 1 / 61, "D": 1 / 63}
    assert [h.evidence_id for h in hits] == ["C", "B", "A", "D"]
    assert {h.evidence_id: h.score for h in hits} == pytest.approx(expected)
    assert all(math.isfinite(h.score) for h in hits)


def test_ties_empty_and_reordering() -> None:
    tied = fuse(("B", "A"), ("A", "B"))
    assert [h.evidence_id for h in tied] == ["A", "B"]
    assert tied[0].score == tied[1].score
    assert fuse((), ()) == ()
    assert [h.evidence_id for h in fuse((), ("B", "A"))] == ["B", "A"]
    assert fuse(("B", "A"), ()) == fuse((), ("B", "A"))
    assert fuse(("A", "B"), ("A", "B"))[0].score == 2 / 61
    assert fuse(("B", "A"), ("B", "A"))[0].evidence_id == "B"
    with pytest.raises(ValueError, match="duplicate"):
        fuse(("A", "A"), ())


@pytest.fixture
def inputs(tmp_path: Path) -> tuple[Path, tuple[SourcePin, ...]]:
    """Eight fictional public questions, 34 fictional evidence units, no gold."""
    artifact = {
        "units": [
            {
                "record": {
                    "evidence_id": f"E{i:02}",
                    "ecosystem_id": "fictional",
                    "content": f"Fictional content {i}",
                    "applicability": "not a ranking input",
                }
            }
            for i in range(34)
        ]
    }
    public = [
        {
            "query_id": f"q:{i}",
            "ecosystem_id": "fictional",
            "query_text": f"Fictional question {i}",
            "query_kind": "lookup",
            "source_version": None,
            "requested_version": {
                "kind": "exact",
                "scheme": "fictional",
                "value": "r1",
            },
        }
        for i in range(8)
    ]
    for name, artifact_value in ((EVIDENCE, artifact), (QUERIES, public)):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(artifact_value))
    snapshot = (
        "retrieval-input:"
        + digest(
            canonical(
                {
                    "documents": [asdict(d) for d in documents_from_artifact(artifact)],
                    "queries": [asdict(q) for q in queries_from_public(public)],
                }
            )
        )[7:]
    )
    hashes = {
        "evidence": digest((tmp_path / EVIDENCE).read_bytes()),
        "public_queries": digest((tmp_path / QUERIES).read_bytes()),
    }
    pins = []
    for pin, order in zip(
        SOURCES, (["E00", "E01", "E02"], ["E02", "E01", "E03"]), strict=True
    ):
        value: dict[str, Any] = {
            "format_version": 1,
            "status": "unscored",
            "run_id": f"fictional:{pin.method}",
            "run_depth": 3,
            "retrieval_input_snapshot": snapshot,
            "artifact_hashes": hashes,
            "results": [
                {"query_id": q["query_id"], "evidence_ids": order} for q in public
            ],
            "diagnostics": [
                {"query_id": q["query_id"], "scores": [3.0, 2.0, 1.0]} for q in public
            ],
        }
        body = json.dumps(value).encode()
        path = tmp_path / pin.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        pins.append(replace(pin, run_id=value["run_id"], content_hash=digest(body)))
    return tmp_path, tuple(pins)


def test_generation_isolated_deterministic_and_nonmutating(
    inputs: tuple[Path, tuple[SourcePin, ...]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, pins = inputs
    allowed = {root / EVIDENCE, root / QUERIES, *(root / p.path for p in pins)}
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in allowed}
    output = root / OUTPUT
    read = Path.read_bytes
    seen = []

    def guarded(path: Path) -> bytes:
        assert path in allowed | {output}, f"forbidden read: {path}"
        seen.append(path)
        return read(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    a = run_development(root, sources=pins)
    saved = (output.read_bytes(), output.stat().st_mtime_ns)
    b = run_development(root, sources=pins)
    assert a == b
    assert saved == (output.read_bytes(), output.stat().st_mtime_ns)
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in allowed}
    assert set(seen) == allowed | {output}
    assert all(
        row["evidence_ids"] == ("E02", "E01", "E00", "E03") for row in a["results"]
    )
    assert a["source_runs"][0]["content_hash"] == pins[0].content_hash


def change_source(
    root: Path, pins: tuple[SourcePin, ...], value: dict[str, Any]
) -> tuple[SourcePin, ...]:
    body = json.dumps(value).encode()
    (root / pins[0].path).write_bytes(body)
    return (replace(pins[0], content_hash=digest(body)), pins[1])


@pytest.mark.parametrize(
    "bad",
    [
        "hash",
        "identity",
        "snapshot",
        "artifacts",
        "missing-query",
        "duplicate-query",
        "unknown-query",
        "duplicate-evidence",
        "unknown-evidence",
        "depth",
        "nonfinite",
        "score-count",
    ],
)
def test_invalid_source_rejected_before_output(
    inputs: tuple[Path, tuple[SourcePin, ...]],
    bad: str,
) -> None:
    root, pins = inputs
    value = json.loads((root / pins[0].path).read_bytes())
    if bad == "hash":
        (root / pins[0].path).write_bytes(b"changed frozen bytes")
    else:
        if bad == "identity":
            value["run_id"] = "different"
        elif bad == "snapshot":
            value["retrieval_input_snapshot"] = "different"
        elif bad == "artifacts":
            value["artifact_hashes"]["evidence"] = "different"
        elif bad == "missing-query":
            value["results"].pop()
        elif bad == "duplicate-query":
            value["results"][0]["query_id"] = value["results"][1]["query_id"]
        elif bad == "unknown-query":
            value["results"][0]["query_id"] = "unknown"
        elif bad == "duplicate-evidence":
            value["results"][0]["evidence_ids"] = ["E00", "E00", "E01"]
        elif bad == "unknown-evidence":
            value["results"][0]["evidence_ids"][0] = "unknown"
        elif bad == "depth":
            value["run_depth"] = 1
        elif bad == "nonfinite":
            value["diagnostics"][0]["scores"][0] = float("nan")
        else:
            value["diagnostics"][0]["scores"] = []
        pins = change_source(root, pins, value)
    with pytest.raises(ValueError):
        run_development(root, sources=pins)
    assert not (root / OUTPUT).exists()


def test_empty_and_different_depths_and_raw_score_independence(
    inputs: tuple[Path, tuple[SourcePin, ...]],
) -> None:
    root, pins = inputs
    before = run_development(root, sources=pins)
    value = json.loads((root / pins[0].path).read_bytes())
    for row in value["diagnostics"]:
        row["scores"] = [9999.0, -123.0, 0.0]
    pins = change_source(root, pins, value)
    after = run_development(root, sources=pins)
    assert before["results"] == after["results"]
    assert before["diagnostics"] == after["diagnostics"]
    assert (
        before["run_id"] != after["run_id"]
    )  # changed source bytes, not rank features
    value["run_depth"] = 1
    for row in value["results"]:
        row["evidence_ids"] = ["E00"]
    for row in value["diagnostics"]:
        row["scores"] = [2.0]
    pins = change_source(root, pins, value)
    assert len(run_development(root, sources=pins)["results"][0]["evidence_ids"]) == 4
    value["run_depth"] = 0
    for row in value["results"]:
        row["evidence_ids"] = []
    for row in value["diagnostics"]:
        row["scores"] = []
    pins = change_source(root, pins, value)
    assert run_development(root, sources=pins)["results"][0]["evidence_ids"] == (
        "E02",
        "E01",
        "E03",
    )


@pytest.mark.parametrize("target", [EVIDENCE, QUERIES])
def test_current_input_changes_rejected(
    inputs: tuple[Path, tuple[SourcePin, ...]],
    target: str,
) -> None:
    root, pins = inputs
    path = root / target
    data = json.loads(path.read_bytes())
    if target == EVIDENCE:
        data["units"][0]["record"]["content"] += " changed"
    else:
        data[0]["query_text"] += " changed"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="snapshot"):
        run_development(root, sources=pins)
