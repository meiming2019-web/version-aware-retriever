"""Fictional applicability tests; real smoke tests check structure, never gold."""

import copy
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from version_aware_retriever.contracts import (
    ApplicabilityAssertion,
    AssertionKind,
    QueryKind,
    SelectorKind,
    VersionSelector,
)
from version_aware_retriever.lexical import RetrievalQuery
from version_aware_retriever.version_aware import (
    EVIDENCE,
    OUTPUT,
    QUERIES,
    SOURCE,
    Classification,
    classify,
    decode_assertion,
    exact_match,
    rerank,
    run_development,
)


def v(value: str) -> VersionSelector:
    return VersionSelector(kind=SelectorKind.EXACT, scheme="fictional", value=value)


def query(source: str | None = None, target: str = "r2") -> RetrievalQuery:
    return RetrievalQuery(
        query_id="fictional:q",
        ecosystem_id="fictional",
        query_text="Fictional scenario",
        query_kind=QueryKind.MIGRATION if source else QueryKind.LOOKUP,
        requested_version=v(target),
        source_version=v(source) if source else None,
    )


def behavior(*versions: str) -> ApplicabilityAssertion:
    return ApplicabilityAssertion(
        kind=AssertionKind.BEHAVIOR,
        content_locator="chars:0:10",
        basis_locator="L1-L1",
        basis="Fictional experimental metadata",
        applies_to=tuple(v(s) for s in versions),
    )


def transition(source: str, target: str) -> ApplicabilityAssertion:
    return ApplicabilityAssertion(
        kind=AssertionKind.TRANSITION,
        content_locator="chars:11:20",
        basis_locator="L2-L2",
        basis="Fictional transition",
        transition_source=(v(source),),
        transition_target=(v(target),),
    )


def test_lookup_tiers_and_stable_original_order() -> None:
    metadata = {
        "unknown": (behavior("r9"),),
        "context": (transition("r1", "r2"),),
        "direct-b": (behavior("r2"),),
        "direct-a": (behavior("r2"),),
    }
    ranking = ("unknown", "direct-b", "context", "direct-a")
    before = copy.deepcopy((ranking, metadata))
    rows = rerank(query(), ranking, metadata)
    assert [r[0] for r in rows] == ["direct-b", "direct-a", "context", "unknown"]
    assert [r[1].tier for r in rows] == [1, 1, 2, 3]
    assert [r[2] for r in rows] == [2, 4, 3, 1]
    assert before == (ranking, metadata)
    assert rows == rerank(query(), ranking, metadata)
    assert rows[-1][1].classification is Classification.UNKNOWN
    assert (
        classify((transition("r2", "r3"),), query()).classification
        is Classification.TRANSITION_RELEVANT
    )


def test_migration_roles_and_mixed_assertions() -> None:
    metadata = {
        "target": (behavior("r2"),),
        "unknown": (behavior("r9"),),
        "source": (behavior("r1"),),
        "both": (behavior("r1"), behavior("r2")),
        "transition": (behavior("r9"), transition("r1", "r2")),
    }
    rows = rerank(query("r1"), tuple(metadata), metadata)
    assert [r[0] for r in rows] == ["transition", "both", "target", "source", "unknown"]
    assert [r[1].tier for r in rows] == [1, 2, 3, 3, 4]
    assert rows[0][1].matched_assertions[0].assertion_index == 1
    assert {m.roles for m in rows[1][1].matched_assertions} == {
        ("source",),
        ("target",),
    }
    assert (
        classify((behavior("r1", "r2"),), query("r1")).classification
        is Classification.SOURCE_AND_TARGET_MATCH
    )
    assert (
        classify((transition("r2", "r1"),), query("r1")).classification
        is Classification.UNKNOWN
    )
    assert (
        classify(
            (transition("r1", "r3"), transition("r3", "r2")), query("r1")
        ).classification
        is Classification.UNKNOWN
    )
    mixed = (transition("r1", "r2"), behavior("r2"), behavior("r9"))
    assert classify(mixed, query()).classification is Classification.DIRECT_MATCH
    assert (
        classify(mixed, query("r1")).classification is Classification.TRANSITION_MATCH
    )


def test_unknown_and_deprecation_never_create_negative_class() -> None:
    deprecated = replace(
        behavior("r1"),
        basis="Fictional deprecated API in older documentation",
        basis_locator="old-document",
        content_locator="incidental scope",
    )
    for assertions in ((), (deprecated,), (behavior("r3"),)):
        relation = classify(assertions, query())
        assert relation.classification is Classification.UNKNOWN
        assert relation.matched_assertions == ()
    assert not any("INVALID" in c.value for c in Classification)


@pytest.mark.parametrize(
    "selector",
    [
        VersionSelector(kind=SelectorKind.UNKNOWN, scheme="fictional"),
        VersionSelector(kind=SelectorKind.RELEASE_LINE, scheme="fictional", value="r2"),
        VersionSelector(
            kind=SelectorKind.RANGE,
            scheme="fictional",
            lower="r1",
            upper="r3",
            lower_inclusive=True,
            upper_inclusive=True,
        ),
        VersionSelector(kind=SelectorKind.EXACT, scheme="another-scheme", value="r2"),
        v("r2.0"),
    ],
)
def test_nonmatching_selector_is_unknown(selector: VersionSelector) -> None:
    assert not exact_match(selector, v("r2"))
    assert (
        classify(
            (replace(behavior("r2"), applies_to=(selector,)),), query()
        ).classification
        is Classification.UNKNOWN
    )


def test_invalid_selectors_and_bad_ids_rejected() -> None:
    assert exact_match(v("r2"), v("r2"))
    data = asdict(behavior("r2"))
    data["applies_to"][0]["kind"] = "invalid-selector"
    with pytest.raises(ValueError):
        decode_assertion(data)
    data = asdict(behavior("r2"))
    data["applies_to"][0]["value"] = None
    with pytest.raises(ValueError):
        decode_assertion(data)
    with pytest.raises(ValueError):
        replace(
            query(),
            requested_version=VersionSelector(
                kind=SelectorKind.UNKNOWN, scheme="fictional"
            ),
        )
    with pytest.raises(ValueError):
        rerank(query(), ("missing",), {})
    with pytest.raises(ValueError):
        rerank(query(), ("same", "same"), {"same": ()})


def test_real_corpus_structural_smoke_and_access_isolation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Uses only unreviewed metadata/public inputs/RRF; asserts no gold ranking."""
    root = Path(__file__).resolve().parents[1]
    input_paths = (EVIDENCE, QUERIES, SOURCE.path)
    original = {
        root / p: ((root / p).read_bytes(), (root / p).stat().st_mtime_ns)
        for p in input_paths
    }
    for name in input_paths:
        destination = tmp_path / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(original[root / name][0])
    read = Path.read_bytes
    allowed = {tmp_path / p for p in (*input_paths, OUTPUT)}
    seen = set()

    def guarded(path: Path) -> bytes:
        assert path in allowed, f"forbidden read: {path}"
        seen.add(path)
        return read(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", guarded)
        report = run_development(tmp_path)
        output = tmp_path / OUTPUT
        before = (output.read_bytes(), output.stat().st_mtime_ns)
        assert report == run_development(tmp_path)
        assert before == (output.read_bytes(), output.stat().st_mtime_ns)
        assert seen == allowed
        source = json.loads((tmp_path / SOURCE.path).read_bytes())
    ids = {
        u["record"]["evidence_id"]
        for u in json.loads(original[root / EVIDENCE][0])["units"]
    }
    assert len(report["results"]) == 8
    for result, diagnostics in zip(
        report["results"], report["diagnostics"], strict=True
    ):
        assert len(result["evidence_ids"]) == 34 and set(result["evidence_ids"]) == ids
        order = next(
            r["evidence_ids"]
            for r in source["results"]
            if r["query_id"] == result["query_id"]
        )
        scores = next(
            r["scores"]
            for r in source["diagnostics"]
            if r["query_id"] == result["query_id"]
        )
        assert sum(diagnostics["tier_counts"].values()) == 34
        for i, item in enumerate(diagnostics["items"]):
            original_rank = order.index(item["evidence_id"]) + 1
            assert item["original_rrf_rank"] == original_rank
            assert (
                item["original_rrf_score"]
                == diagnostics["scores"][i]
                == scores[original_rank - 1]
            )
        assert [
            (i["tier"], i["original_rrf_rank"]) for i in diagnostics["items"]
        ] == sorted((i["tier"], i["original_rrf_rank"]) for i in diagnostics["items"])
    assert original == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in original}
