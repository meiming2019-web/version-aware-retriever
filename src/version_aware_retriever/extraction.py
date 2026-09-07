"""Offline explicit-span extraction. Upstream documentation is never executed."""

import argparse
import json
import os
import tempfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any

from version_aware_retriever.acquisition import (
    checked_file,
    decode_record,
    digest,
    read_selection,
    require,
    verify,
)
from version_aware_retriever.contracts import (
    ApplicabilityAssertion,
    AssertionKind,
    ContributionRole,
    DocumentType,
    EvidenceUnit,
    Record,
    SelectorKind,
    SourceContribution,
    SourceManifestEntry,
    VersionSelector,
)

FORMATTING = {"", "\n", "```python\n", "\n```python\n", "```\n", "\n```\n"}


def canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def physical_lines(text: str) -> list[str]:
    parts = text.split("\n")
    return [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


@dataclass(frozen=True, kw_only=True)
class Span(Record):
    source_id: str
    first: int
    last: int

    def __post_init__(self) -> None:
        super().__post_init__()
        require(1 <= self.first <= self.last, "invalid source line span")

    @property
    def locator(self) -> str:
        return f"L{self.first}-L{self.last}"


@dataclass(frozen=True)
class SourceText:
    record: SourceManifestEntry
    path: str
    text: str
    allowed_lines: tuple[tuple[int, int], ...]
    companion_of: str | None = None

    def read(self, span: Span) -> str:
        require(span.source_id == self.record.source_id, "source reference mismatch")
        lines = physical_lines(self.text)
        require(span.last <= len(lines), "source span out of range")
        require(
            any(a <= span.first <= span.last <= b for a, b in self.allowed_lines),
            "disallowed source span",
        )
        return "".join(lines[span.first - 1 : span.last])


def source_span(data: dict[str, Any]) -> Span:
    return Span(source_id=data["source_id"], first=data["first"], last=data["last"])


def read_span(span: Span, sources: dict[str, SourceText]) -> str:
    require(span.source_id in sources, "unknown source reference")
    return sources[span.source_id].read(span)


def assemble(
    spec: dict[str, Any], sources: dict[str, SourceText], policy: dict[str, str]
) -> EvidenceUnit:
    """Build one record from reviewed recipe choices; validate their structure."""
    require(policy["revision"] == "explicit-lines-v1", "unsupported assembly policy")
    require(spec["review_status"] == "pending_human_review", "unsupported review claim")
    require(bool(spec["parts"]), "unit requires source parts")
    primary_id = spec["primary_source_id"]
    require(primary_id in sources, "unknown primary source")
    primary = sources[primary_id]
    require(
        primary.record.document_type is not DocumentType.DOCUMENTATION_EXAMPLE,
        "companion cannot be a standalone primary unit",
    )
    headings = [primary.path]
    last_heading = 0
    previous_level = 0
    lines = physical_lines(primary.text)
    for number in spec["heading_lines"]:
        require(
            type(number) is int and last_heading < number <= len(lines),
            "invalid heading locator",
        )
        heading = lines[number - 1].rstrip("\r\n")
        level = len(heading) - len(heading.lstrip("#"))
        require(
            0 < level <= 6
            and level > previous_level
            and heading[level : level + 1] == " ",
            "invalid heading ancestry",
        )
        headings.append(heading[level + 1 :])
        last_heading, previous_level = number, level

    contributions: list[SourceContribution] = []
    copied: list[tuple[Span, int]] = []
    chunks: list[str] = []
    length = 0
    for part in spec["parts"]:
        span = source_span(part)
        original = read_span(span, sources)
        require("{!" not in original, "unmapped include marker in content")
        source = sources[span.source_id]
        require(
            source.record.ecosystem_id == primary.record.ecosystem_id,
            "source/evidence ecosystem mismatch",
        )
        role = ContributionRole(part["role"])
        require(
            (role is ContributionRole.COMPANION_EXAMPLE)
            == (source.record.document_type is DocumentType.DOCUMENTATION_EXAMPLE),
            "contribution role/source type mismatch",
        )
        if role is ContributionRole.COMPANION_EXAMPLE:
            require(
                source.companion_of == primary_id, "unapproved companion attachment"
            )
        prefix, suffix = part["prefix"], part["suffix"]
        require(
            prefix in FORMATTING and suffix in FORMATTING,
            "undeclared formatting transformation",
        )
        chunk = prefix + original + suffix
        require(bool(chunk), "empty source contribution")
        contributions.append(
            SourceContribution(
                source_id=span.source_id,
                source_locator=span.locator,
                role=role,
                content_start=length,
                content_end=length + len(chunk),
            )
        )
        copied.append((span, length + len(prefix)))
        chunks.append(chunk)
        length += len(chunk)

    attached = {
        c.source_id
        for c in contributions
        if c.role is ContributionRole.COMPANION_EXAMPLE
    }
    mapped: set[str] = set()
    marker_locations: set[Span] = set()
    for mapping in spec["includes"]:
        marker = source_span(mapping)
        require(
            marker.source_id == primary_id and marker.first == marker.last,
            "include marker must be one primary-source line",
        )
        require(marker not in marker_locations, "duplicate include mapping")
        marker_locations.add(marker)
        companion_id = mapping["companion_source_id"]
        require(companion_id in attached, "unused or unknown include companion")
        name = PurePosixPath(sources[companion_id].path).stem
        require(
            read_span(marker, sources).strip() == f"{{!.tmp_examples/{name}.md!}}",
            "include marker does not match approved companion",
        )
        mapped.add(companion_id)
    require(mapped == attached, "unmapped companion include")

    def locate(claim: Span) -> str:
        read_span(claim, sources)
        matches = [
            (span, offset)
            for span, offset in copied
            if span.source_id == claim.source_id
            and span.first <= claim.first <= claim.last <= span.last
        ]
        require(len(matches) == 1, "claim must resolve to exactly one copied span")
        span, offset = matches[0]
        source_lines = physical_lines(sources[span.source_id].text)
        start = offset + len("".join(source_lines[span.first - 1 : claim.first - 1]))
        end = start + len(read_span(claim, sources))
        return f"chars:{start}:{end}"

    endpoints = {s.record.document_version.value for s in sources.values()}

    def selectors(values: list[str]) -> tuple[VersionSelector, ...]:
        require(
            all(v == "unknown" or v in endpoints for v in values),
            "applicability outside selected endpoints",
        )
        return tuple(
            VersionSelector(
                kind=SelectorKind.UNKNOWN if v == "unknown" else SelectorKind.EXACT,
                scheme=primary.record.document_version.scheme,
                value=None if v == "unknown" else v,
            )
            for v in values
        )

    assertions = []
    for annotation in spec["assertions"]:
        basis = source_span(annotation["basis_location"])
        read_span(basis, sources)
        require(
            basis.source_id in {c.source_id for c in contributions},
            "basis must belong to a contributing source",
        )
        assertions.append(
            ApplicabilityAssertion(
                kind=AssertionKind(annotation["kind"]),
                content_locator=locate(source_span(annotation["claim"])),
                basis_source_id=basis.source_id,
                basis_locator=basis.locator,
                basis=annotation["basis"],
                applies_to=selectors(annotation["applies_to"]),
                transition_source=selectors(annotation["transition_source"]),
                transition_target=selectors(annotation["transition_target"]),
            )
        )
    primary_parts = [
        c for c in contributions if c.role is ContributionRole.PRIMARY_EXPLANATION
    ]
    require(len(primary_parts) == 1, "exactly one primary explanation required")
    content = "".join(chunks)
    record = EvidenceUnit(
        evidence_id="pending",
        source_id=primary_id,
        ecosystem_id=primary.record.ecosystem_id,
        content=content,
        content_hash=digest(content.encode("utf-8")),
        section_path=tuple(headings),
        source_locator=primary_parts[0].source_locator,
        applicability=tuple(assertions),
        curator_notes="Pending human review. " + " ".join(spec["notes"]),
        contributions=tuple(contributions),
        assembly_policy=policy["revision"],
    )
    source_hashes = {
        c.source_id: sources[c.source_id].record.content_hash for c in contributions
    }
    identity = {
        "record": asdict(record),
        "policy": policy,
        "parts": spec["parts"],
        "includes": spec["includes"],
        "source_hashes": source_hashes,
    }
    return replace(record, evidence_id="evidence:" + digest(canonical(identity))[7:])


def prepare(
    recipe_path: Path, selection: Path, frozen: Path
) -> tuple[dict[str, Any], dict[str, SourceText], list[tuple[str, EvidenceUnit]]]:
    verify(selection, frozen)
    recipe = json.loads(recipe_path.read_bytes())
    require(recipe["format_version"] == 1, "unsupported recipe format")
    require(
        recipe["selection_hash"] == digest(selection.read_bytes()),
        "recipe/selection hash mismatch",
    )
    selected = {item.identity: item for item in read_selection(selection)}
    manifest = json.loads(checked_file(frozen, "manifest.json"))
    require(set(recipe["sources"]) == set(selected), "recipe source registry mismatch")
    sources = {}
    for row in manifest["sources"]:
        record = decode_record(row["record"])
        item = selected[record.source_id]
        companion = next(
            (
                s.identity
                for s in selected.values()
                if s.path == item.companion_of and s.commit == item.commit
            ),
            None,
        )
        text = checked_file(frozen, row["retained_path"]).decode("utf-8")
        require(
            digest(text.encode("utf-8")) == record.content_hash,
            "source changed during extraction",
        )
        allowed = tuple(
            tuple(pair) for pair in recipe["sources"][record.source_id]["allowed_lines"]
        )
        for first, last in allowed:
            span = Span(source_id=record.source_id, first=first, last=last)
            require(
                span.last <= len(physical_lines(text)), "allowlist span out of range"
            )
        sources[record.source_id] = SourceText(
            record, item.path, text, allowed, companion
        )
    records = [
        (spec["key"], assemble(spec, sources, recipe["policy"]))
        for spec in recipe["units"]
    ]
    require(0 < len(records) <= 48, "evidence count must be between 1 and 48")
    require(len({k for k, _ in records}) == len(records), "duplicate recipe key")
    require(
        len({r.evidence_id for _, r in records}) == len(records),
        "duplicate evidence ID",
    )
    migration_count = sum(
        sources[r.source_id].record.document_type is DocumentType.MIGRATION_GUIDE
        for _, r in records
    )
    require(migration_count * 4 <= len(records), "migration share exceeds 25%")
    return recipe, sources, sorted(records)


def render_report(
    recipe: dict[str, Any],
    sources: dict[str, SourceText],
    records: list[tuple[str, EvidenceUnit]],
) -> bytes:
    snapshots = Counter(
        sources[r.source_id].record.document_version.value for _, r in records
    )
    types = Counter(sources[r.source_id].record.document_type.value for _, r in records)
    compound = sum(len({c.source_id for c in r.contributions}) > 1 for _, r in records)
    unknown = [
        k
        for k, r in records
        if any(
            s.kind is SelectorKind.UNKNOWN
            for a in r.applicability
            for s in (*a.applies_to, *a.transition_source, *a.transition_target)
        )
    ]
    duplicates: dict[str, list[str]] = defaultdict(list)
    for key, record in records:
        duplicates[record.content_hash].append(key)
    groups = [keys for keys in duplicates.values() if len(keys) > 1]
    migration = types[DocumentType.MIGRATION_GUIDE.value]
    contributing = {c.source_id for _, r in records for c in r.contributions}
    summary = {
        "total_units": len(records),
        "contributing_physical_sources": len(contributing),
        "contributing_source_types": dict(
            Counter(sources[sid].record.document_type.value for sid in contributing)
        ),
        "by_primary_document_snapshot": dict(snapshots),
        "by_primary_source_type": dict(types),
        "migration_units": migration,
        "migration_share": migration / len(records),
        "compound_units": compound,
        "single_source_units": len(records) - compound,
        "pending_human_review": len(records),
        "unknown_applicability_units": unknown,
        "exact_duplicate_content_groups": groups,
    }
    out = [
        "# Extracted evidence inspection\n\n",
        "Status: mechanically verified extraction; "
        "all applicability is pending human review.\n",
        "No queries or gold labels exist. "
        "Quoted outputs are upstream text, never executed here.\n\n",
        "```json\n",
        pretty(summary).decode(),
        "```\n\n",
        "## Selection coverage and limitations\n\n",
    ]
    out.extend(f"- {note}\n" for note in (*recipe["omissions"], *recipe["issues"]))
    for key, record in records:
        spec = next(unit for unit in recipe["units"] if unit["key"] == key)
        out.extend(
            [
                f"\n## {key}\n\n",
                f"Evidence ID: `{record.evidence_id}`\n\n",
                "Original sources "
                "(document versions are not applicability labels):\n\n",
            ]
        )
        for sid in sorted({c.source_id for c in record.contributions}):
            source = sources[sid]
            out.append(
                f"- `{sid}`: [{source.path}]({source.record.canonical_url}); "
                f"snapshot {source.record.document_version.value}; "
                f"{source.record.content_hash}\n"
            )
        out.extend(
            [
                "\nFull assembled content, quoted as data:\n\n````text\n",
                record.content,
                "\n````\n\nProvenance and proposed applicability:\n\n```json\n",
                pretty(
                    {k: v for k, v in asdict(record).items() if k != "content"}
                ).decode(),
                "```\n",
            ]
        )
        out.extend(
            [
                "\nDeclared source assembly and marker replacements:\n\n```json\n",
                pretty({"parts": spec["parts"], "includes": spec["includes"]}).decode(),
                "```\n",
            ]
        )
    return "".join(out).encode("utf-8")


def artifacts(recipe_path: Path, selection: Path, frozen: Path) -> dict[str, bytes]:
    recipe, sources, records = prepare(recipe_path, selection, frozen)
    return {
        "evidence.json": pretty(
            {
                "format_version": 1,
                "recipe_hash": digest(recipe_path.read_bytes()),
                "selection_hash": recipe["selection_hash"],
                "policy": recipe["policy"],
                "units": [
                    {"key": key, "record": asdict(record)} for key, record in records
                ],
            }
        ),
        "inspection.md": render_report(recipe, sources, records),
    }


def build(
    recipe: Path, selection: Path, frozen: Path, output: Path, *, check: bool = False
) -> None:
    require(
        not output.resolve().is_relative_to(frozen.resolve()),
        "derived output must be outside frozen archive",
    )
    expected = artifacts(recipe, selection, frozen)
    if check:
        for name, body in expected.items():
            require(checked_file(output, name) == body, "derived artifact mismatch")
        return
    require(
        not any(p.is_symlink() for p in (output, *output.parents)),
        "derived output must not use symlinks",
    )
    output.mkdir(parents=True, exist_ok=True)
    for name, body in expected.items():
        target = output / name
        require(not target.is_symlink(), "derived artifact must not be a symlink")
        if target.exists() and target.read_bytes() == body:
            continue
        with tempfile.NamedTemporaryFile(dir=output, delete=False) as temporary:
            temporary.write(body)
            temporary_path = Path(temporary.name)
        try:
            os.replace(temporary_path, target)
        finally:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument(
        "--recipe", type=Path, default=Path("data/pydantic/extraction/recipe.json")
    )
    parser.add_argument(
        "--selection", type=Path, default=Path("data/pydantic/selection.json")
    )
    parser.add_argument("--frozen", type=Path, default=Path("data/pydantic/frozen"))
    parser.add_argument(
        "--output", type=Path, default=Path("data/pydantic/extraction/derived")
    )
    args = parser.parse_args()
    build(
        args.recipe,
        args.selection,
        args.frozen,
        args.output,
        check=args.command == "verify",
    )
    print(
        f"{args.command}: evidence and inspection artifacts match the verified recipe; "
        "human applicability review pending"
    )


if __name__ == "__main__":
    main()
