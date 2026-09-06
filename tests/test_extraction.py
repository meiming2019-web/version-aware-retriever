"""Synthetic assembly tests and separate, offline real-corpus fidelity checks."""

import copy
import json
import shutil
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.acquisition import digest
from version_aware_retriever.contracts import (
    ContractError,
    DocumentType,
    SelectorKind,
    SourceManifestEntry,
    VersionSelector,
)
from version_aware_retriever.extraction import (
    SourceText,
    Span,
    artifacts,
    assemble,
    build,
    physical_lines,
    prepare,
)

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "data/pydantic/selection.json"
FROZEN = ROOT / "data/pydantic/frozen"
RECIPE = ROOT / "data/pydantic/extraction/recipe.json"
POLICY = {"revision": "explicit-lines-v1", "snapshot_policy": "synthetic endpoint only"}


def synthetic_source(
    identity: str, path: str, text: str, *, companion: bool = False
) -> SourceText:
    record = SourceManifestEntry(
        source_id=identity,
        ecosystem_id="synthetic:widget",
        document_type=DocumentType.DOCUMENTATION_EXAMPLE
        if companion
        else DocumentType.CONCEPTUAL_GUIDE,
        title=path,
        canonical_url="https://example.invalid/test-only",
        snapshot_locator="fixture:test-only",
        content_hash=digest(text.encode()),
        document_version=VersionSelector(
            kind=SelectorKind.EXACT, scheme="synthetic", value="r1"
        ),
        captured_at=datetime(2026, 1, 1, tzinfo=UTC),
        publisher="Synthetic",
        license="Test only",
        transformation_record="Test fixture",
    )
    return SourceText(
        record,
        path,
        text,
        ((1, len(physical_lines(text))),),
        "synthetic:doc" if companion else None,
    )


@pytest.fixture
def sources() -> dict[str, SourceText]:
    return {
        "synthetic:doc": synthetic_source(
            "synthetic:doc",
            "guide.md",
            "# Topic\nQualifier: café, only when enabled.\n\n"
            "{!.tmp_examples/example.md!}\n\n"
            "| name | value |\n|---|---|\n| é | stable |\n",
        ),
        "synthetic:example": synthetic_source(
            "synthetic:example",
            "example.py",
            "if True:\n    value = 'é'\n",
            companion=True,
        ),
    }


@pytest.fixture
def spec() -> dict[str, Any]:
    return {
        "key": "test-only",
        "primary_source_id": "synthetic:doc",
        "heading_lines": [1],
        "parts": [
            {
                "source_id": "synthetic:doc",
                "first": 1,
                "last": 2,
                "role": "primary_explanation",
                "prefix": "",
                "suffix": "",
            }
        ],
        "includes": [],
        "review_status": "pending_human_review",
        "notes": [],
        "assertions": [
            {
                "kind": "behavior",
                "claim": {"source_id": "synthetic:doc", "first": 2, "last": 2},
                "basis_location": {"source_id": "synthetic:doc", "first": 2, "last": 2},
                "basis": "Synthetic fixture assertion, not benchmark gold.",
                "applies_to": ["r1"],
                "transition_source": [],
                "transition_target": [],
            }
        ],
    }


def attach(spec: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(spec)
    result["parts"].extend(
        [
            {
                "source_id": "synthetic:example",
                "first": 1,
                "last": 2,
                "role": "companion_example",
                "prefix": "```python\n",
                "suffix": "```\n",
            },
            {
                "source_id": "synthetic:doc",
                "first": 5,
                "last": 8,
                "role": "supporting_explanation",
                "prefix": "",
                "suffix": "",
            },
        ]
    )
    result["includes"] = [
        {
            "source_id": "synthetic:doc",
            "first": 4,
            "last": 4,
            "companion_source_id": "synthetic:example",
        }
    ]
    return result


def test_single_source_and_unicode(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    record = assemble(spec, sources, POLICY)
    assert record.content == "# Topic\nQualifier: café, only when enabled.\n"
    assert record.content_hash == digest(record.content.encode("utf-8"))
    assert record.contributions[0].content_end == len(record.content)
    assert record.contributions[0].content_end != len(record.content.encode())
    assert record.applicability[0].content_locator == f"chars:8:{len(record.content)}"
    assert record.applicability[0].basis_source_id == "synthetic:doc"
    assert record.applicability[0].basis_locator == "L2-L2"


def test_compound_preserves_code_qualifiers_and_table(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    record = assemble(attach(spec), sources, POLICY)
    assert record.content == (
        "# Topic\nQualifier: café, only when enabled.\n"
        "```python\nif True:\n    value = 'é'\n```\n"
        "\n| name | value |\n|---|---|\n| é | stable |\n"
    )
    assert "{!" not in record.content
    assert len(record.contributions) == 3
    assert all(
        a.content_end == b.content_start
        for a, b in zip(record.contributions, record.contributions[1:])
    )


@pytest.mark.parametrize(
    "field,value", [("source_id", "missing"), ("first", 0), ("last", 99)]
)
def test_invalid_spans(
    spec: dict[str, Any], sources: dict[str, SourceText], field: str, value: object
) -> None:
    spec["parts"][0][field] = value
    with pytest.raises(ContractError):
        assemble(spec, sources, POLICY)


def test_disallowed_span(spec: dict[str, Any], sources: dict[str, SourceText]) -> None:
    sources["synthetic:doc"] = replace(
        sources["synthetic:doc"], allowed_lines=((1, 1),)
    )
    with pytest.raises(ContractError, match="disallowed"):
        assemble(spec, sources, POLICY)


def test_unmapped_include(spec: dict[str, Any], sources: dict[str, SourceText]) -> None:
    spec["parts"][0]["last"] = 4
    with pytest.raises(ContractError, match="unmapped include"):
        assemble(spec, sources, POLICY)


def test_attachment_requires_mapping(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    compound = attach(spec)
    compound["includes"] = []
    with pytest.raises(ContractError, match="unmapped companion"):
        assemble(compound, sources, POLICY)
    sources["synthetic:example"] = replace(
        sources["synthetic:example"], companion_of="other"
    )
    with pytest.raises(ContractError, match="unapproved companion"):
        assemble(attach(spec), sources, POLICY)


def test_invalid_basis_and_ambiguous_claim(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    spec["assertions"][0]["basis_location"]["source_id"] = "synthetic:example"
    with pytest.raises(ContractError, match="contributing source"):
        assemble(spec, sources, POLICY)
    spec["assertions"][0]["basis_location"]["source_id"] = "synthetic:doc"
    spec["parts"].append({**spec["parts"][0], "role": "supporting_explanation"})
    with pytest.raises(ContractError, match="exactly one copied span"):
        assemble(spec, sources, POLICY)


def test_unknown_and_endpoint_restriction(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    spec["assertions"][0]["applies_to"] = ["unknown"]
    record = assemble(spec, sources, POLICY)
    assert record.applicability[0].applies_to[0].kind is SelectorKind.UNKNOWN
    spec["assertions"][0]["applies_to"] = ["future"]
    with pytest.raises(ContractError, match="selected endpoints"):
        assemble(spec, sources, POLICY)


def test_identity_inputs(spec: dict[str, Any], sources: dict[str, SourceText]) -> None:
    original = assemble(spec, sources, POLICY)
    assert assemble(copy.deepcopy(spec), sources, POLICY) == original
    assert (
        assemble(spec, sources, {**POLICY, "snapshot_policy": "changed"}).evidence_id
        != original.evidence_id
    )
    changed = copy.deepcopy(spec)
    changed["assertions"][0]["basis"] += " Revised annotation."
    assert assemble(changed, sources, POLICY).evidence_id != original.evidence_id
    changed["assertions"] = spec["assertions"]
    changed["parts"][0]["suffix"] = "\n"
    assert assemble(changed, sources, POLICY).evidence_id != original.evidence_id
    source = sources["synthetic:doc"]
    sources["synthetic:doc"] = replace(
        source,
        record=replace(source.record, captured_at=datetime(2025, 1, 1, tzinfo=UTC)),
    )
    assert assemble(spec, sources, POLICY).evidence_id == original.evidence_id


def test_same_content_different_selected_span_changes_identity(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    text = "# Topic\nSame claim.\nSame claim.\n"
    sources["synthetic:doc"] = synthetic_source("synthetic:doc", "guide.md", text)
    spec["parts"][0].update(first=2, last=2)
    first = assemble(spec, sources, POLICY)
    spec["parts"][0].update(first=3, last=3)
    for field in ("claim", "basis_location"):
        spec["assertions"][0][field].update(first=3, last=3)
    second = assemble(spec, sources, POLICY)
    assert first.content == second.content
    assert first.evidence_id != second.evidence_id


def test_source_snapshot_changes_identity(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    original = assemble(spec, sources, POLICY)
    source = sources.pop("synthetic:doc")
    new_id = "synthetic:new-snapshot"
    sources[new_id] = replace(
        source,
        record=replace(
            source.record, source_id=new_id, snapshot_locator="fixture:new-snapshot"
        ),
    )
    changed = json.loads(json.dumps(spec).replace("synthetic:doc", new_id))
    new = assemble(changed, sources, POLICY)
    assert original.content == new.content
    assert original.evidence_id != new.evidence_id


def test_no_technical_text_insertions(
    spec: dict[str, Any], sources: dict[str, SourceText]
) -> None:
    spec["parts"][0]["prefix"] = "Invented claim."
    with pytest.raises(ContractError, match="formatting"):
        assemble(spec, sources, POLICY)


def test_real_corpus_representatives() -> None:
    _, sources, records = prepare(RECIPE, SELECTION, FROZEN)
    by_key = dict(records)
    required = by_key["v1-required"]
    assert len({c.source_id for c in required.contributions}) == 2
    assert "    a: int\n    b: int = ...\n    c: int = Field(...)" in required.content
    assert "will not work well" in required.content
    v2 = by_key["v2-validator-errors"]
    assert v2.content == sources[v2.source_id].read(
        Span(source_id=v2.source_id, first=468, last=472)
    )
    assert "not wrapped in a `ValidationError`" in v2.content
    migration = by_key["migration-methods"]
    assert migration.content == sources[migration.source_id].read(
        Span(source_id=migration.source_id, first=78, last=95)
    )
    assert "| `dict()` | `model_dump()` |" in migration.content
    assert "DeprecationWarning" in migration.content
    assert len(records) == 34
    for key in ("v1-parse-obj", "v2-model-validate"):
        assert all(
            token not in by_key[key].content
            for token in (
                "parse_raw",
                "parse_file",
                "model_validate_json",
                "write_text",
            )
        )
    for _, record in records:
        assert record.content_hash == digest(record.content.encode())
        assert "{!" not in record.content


def test_real_build_is_deterministic_and_does_not_rewrite(tmp_path: Path) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    build(RECIPE, SELECTION, FROZEN, first)
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in first.iterdir()}
    build(RECIPE, SELECTION, FROZEN, first)
    assert before == {
        p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in first.iterdir()
    }
    build(RECIPE, SELECTION, FROZEN, second)
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {
        p.name: p.read_bytes() for p in second.iterdir()
    }
    build(RECIPE, SELECTION, FROZEN, first, check=True)


def test_corrupt_frozen_input_blocks_publication(tmp_path: Path) -> None:
    frozen = tmp_path / "frozen"
    shutil.copytree(FROZEN, frozen)
    manifest = json.loads((frozen / "manifest.json").read_bytes())
    (frozen / manifest["sources"][0]["retained_path"]).write_bytes(
        b"synthetic corruption"
    )
    output = tmp_path / "derived"
    with pytest.raises(ContractError, match="hash mismatch"):
        build(RECIPE, SELECTION, frozen, output)
    assert not output.exists()


def test_checked_in_artifacts_match_recipe() -> None:
    expected = artifacts(RECIPE, SELECTION, FROZEN)
    for name, content in expected.items():
        assert (RECIPE.parent / "derived" / name).read_bytes() == content
