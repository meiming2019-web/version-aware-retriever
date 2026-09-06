"""Fictional arithmetic/isolation fixtures; real smoke tests assert no gold order."""

import copy
import json
import math
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.contracts import ContractError
from version_aware_retriever.lexical import (
    BM25Index,
    Document,
    documents_from_artifact,
    project_queries,
    queries_from_public,
    run_development,
    tokenize,
)


def docs(*texts: str) -> tuple[Document, ...]:
    return tuple(
        Document(f"D{i}", "fictional:widget", t) for i, t in enumerate(texts, 1)
    )


def test_hand_arithmetic() -> None:
    index = BM25Index(docs("alpha alpha", "alpha beta", "gamma delta"))
    hits = index.search("alpha")
    assert [h.evidence_id for h in hits] == ["D1", "D2"]
    # df=2 documents, not three occurrences; lengths are equal.
    assert hits[0].score == pytest.approx(4.4 / 3.2 * math.log(1.6))
    assert hits[1].score == pytest.approx(math.log(1.6))
    assert index.search("alpha alpha ALPHA") == hits
    assert index.search("alpha", 10) == hits
    assert len(index.search("alpha", 1)) == 1


def test_length_and_saturation() -> None:
    hits = BM25Index(docs("x", "x x x", "x a b c d")).search("x")
    scores = {h.evidence_id: h.score for h in hits}
    # N=df=3, avgdl=3. Length-normalized denominators, calculated independently.
    idf = math.log(1 + 0.5 / 3.5)
    assert scores["D1"] == pytest.approx(idf * 2.2 / 1.6)
    assert scores["D2"] == pytest.approx(idf * 6.6 / 4.2)
    assert scores["D3"] == pytest.approx(idf * 2.2 / 2.8)
    assert scores["D2"] < 3 * scores["D1"]


def test_tokens() -> None:
    assert tokenize("model_dump TypeError BaseModel.model_dump STRAẞE café 中文") == (
        "model_dump",
        "typeerror",
        "basemodel",
        "model_dump",
        "strasse",
        "café",
        "中文",
    )


@pytest.mark.parametrize("query", ["", "...!", "outofvocabulary"])
def test_no_matches(query: str) -> None:
    assert BM25Index(docs("alpha")).search(query) == ()
    assert BM25Index(()).search(query) == ()
    assert BM25Index(docs("", "!!!")).search(query) == ()


def test_ties_and_immutability() -> None:
    documents = (
        Document("Z", "fictional:x", "same"),
        Document("A", "fictional:x", "same"),
    )
    before = copy.deepcopy(documents)
    index = BM25Index(documents)
    assert [h.evidence_id for h in index.search("same")] == ["A", "Z"]
    assert index.search("same") == index.search("same")
    assert documents == before
    assert index.search("same", 0) == ()
    with pytest.raises(ContractError):
        BM25Index((documents[0], documents[0]))


@pytest.mark.parametrize("k", [-1, True, 1.5, "3"])
def test_bad_limit(k: object) -> None:
    with pytest.raises(ContractError):
        BM25Index(docs("x")).search("x", k)  # type: ignore[arg-type]


def public_fixture() -> list[dict[str, object]]:
    return [
        {
            "query_id": f"fictional:{i}",
            "ecosystem_id": "fictional:widget",
            "query_text": "alpha",
            "query_kind": "lookup",
            "source_version": None,
            "requested_version": {"kind": "exact", "scheme": "test", "value": "r1"},
        }
        for i in range(8)
    ]


def test_projection_and_annotation_isolation() -> None:
    public = public_fixture()
    draft: dict[str, Any] = {
        "queries": [
            {
                "retriever_input": q,
                "curation": {"answerability": "secret", "candidates": ["D1"]},
            }
            for q in public
        ]
    }
    before = copy.deepcopy(draft)
    projected = project_queries(draft)
    draft["queries"][0]["curation"] = {
        "answerability": "opposite",
        "candidates": ["D2"],
    }
    assert project_queries(draft) == projected == public
    assert set(projected[0]) == set(public[0])
    assert before["queries"][0]["retriever_input"] == projected[0]
    artifact: dict[str, Any] = {
        "units": [
            {
                "key": "secret",
                "record": {
                    "evidence_id": "D1",
                    "ecosystem_id": "fictional:widget",
                    "content": "alpha",
                    "curator_notes": "secret",
                    "applicability": "secret",
                },
            }
        ]
    }
    documents = documents_from_artifact(artifact)
    assert BM25Index(documents).search("secret") == ()
    artifact["units"][0]["record"]["curator_notes"] = "different alpha"
    assert documents_from_artifact(artifact) == documents
    assert BM25Index(documents).search(projected[0]["query_text"]) == BM25Index(
        documents_from_artifact(artifact)
    ).search(project_queries(draft)[0]["query_text"])
    queries_from_public(projected)
    with pytest.raises(ContractError):
        queries_from_public([projected[0], projected[0]])
    with pytest.raises(ContractError):
        queries_from_public([{**projected[0], "answerability": "secret"}])
    with pytest.raises(ContractError):
        queries_from_public(
            [{k: v for k, v in projected[0].items() if k != "requested_version"}]
        )
    with pytest.raises(ContractError):
        documents_from_artifact({"units": [{"record": {}}]})


def test_runner_reads_only_public_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    evidence, queries, output = (
        tmp_path / n for n in ("evidence.json", "public.json", "run.json")
    )
    evidence.write_text(
        json.dumps(
            {
                "units": [
                    {
                        "record": {
                            "evidence_id": "D1",
                            "ecosystem_id": "fictional:widget",
                            "content": "alpha",
                        }
                    }
                ]
            }
        )
    )
    queries.write_text(json.dumps(public_fixture()))
    original = Path.read_bytes
    opened = []

    def guarded(path: Path) -> bytes:
        assert path in (evidence, queries, output)
        opened.append(path)
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    first = run_development(evidence, queries, output)
    state = (output.read_bytes(), output.stat().st_mtime_ns)
    assert run_development(evidence, queries, output) == first
    assert state == (output.read_bytes(), output.stat().st_mtime_ns)
    assert set(opened) == {evidence, queries, output}
    assert len(first["results"]) == 8 and first["status"] == "unscored"
    assert "benchmark_revision" not in first
    queries.write_text(json.dumps(public_fixture()[:7]))
    with pytest.raises(ContractError):
        run_development(evidence, queries, output)


def test_real_public_smoke(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "data/pydantic/extraction/derived/evidence.json"
    queries = root / "data/pydantic/benchmark/queries.dev.input.json"
    output = tmp_path / "run.json"
    report = run_development(evidence, queries, output)
    state = (output.read_bytes(), output.stat().st_mtime_ns)
    assert run_development(evidence, queries, output) == report
    assert state == (output.read_bytes(), output.stat().st_mtime_ns)
    known = {
        d.evidence_id
        for d in documents_from_artifact(json.loads(evidence.read_bytes()))
    }
    assert len(known) == report["run_depth"] == 34
    assert len(report["results"]) == 8
    for r, diagnostic in zip(report["results"], report["diagnostics"], strict=True):
        assert set(r["evidence_ids"]) <= known
        assert len(r["evidence_ids"]) == len(diagnostic["scores"])
        assert all(math.isfinite(s) and s > 0 for s in diagnostic["scores"])
