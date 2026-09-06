"""Ecosystem-neutral, immutable benchmark records and validation.

IDs are opaque, persistent identifiers assigned by the producer. Validation checks
their form and references, not their stability across builds. Hash verification,
version ordering, source acquisition, retrieval, and scoring are outside this module.
"""

from dataclasses import dataclass, fields
from datetime import datetime
from enum import StrEnum
from types import UnionType
from typing import get_args, get_origin, get_type_hints


class ContractError(ValueError):
    """A record or collection violates the benchmark contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _matches(value: object, annotation: object) -> bool:
    """Check the small set of runtime types used by these record contracts."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is UnionType:
        return any(_matches(value, member) for member in args)
    if origin is tuple:
        return isinstance(value, tuple) and all(
            _matches(item, args[0]) for item in value
        )
    if annotation is int:
        return type(value) is int
    if annotation is bool:
        return type(value) is bool
    return isinstance(annotation, type) and isinstance(value, annotation)


@dataclass(frozen=True, kw_only=True)
class Record:
    """Reject invalid runtime types and blank text, including tuple members."""

    def __post_init__(self) -> None:
        hints = get_type_hints(type(self))
        for field in fields(self):
            value = getattr(self, field.name)
            _require(_matches(value, hints[field.name]), f"{field.name}: invalid type")
            values = value if isinstance(value, tuple) else (value,)
            for item in values:
                if isinstance(item, str):
                    _require(bool(item.strip()), f"{field.name}: blank text")
            if value is not None and (
                field.name.endswith("_id") or field.name == "benchmark_revision"
            ):
                _require(
                    isinstance(value, str) and not any(c.isspace() for c in value),
                    f"{field.name}: identifiers must not contain whitespace",
                )


class SelectorKind(StrEnum):
    EXACT = "exact"
    RANGE = "range"
    RELEASE_LINE = "release_line"
    UNKNOWN = "unknown"


@dataclass(frozen=True, kw_only=True)
class VersionSelector(Record):
    kind: SelectorKind
    scheme: str
    value: str | None = None
    lower: str | None = None
    upper: str | None = None
    lower_inclusive: bool | None = None
    upper_inclusive: bool | None = None
    open_bound_basis: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.kind is SelectorKind.RANGE:
            _require(self.value is None, "range cannot have value")
            _require(
                self.lower is not None or self.upper is not None,
                "range requires at least one bound",
            )
            for bound, inclusive in (
                (self.lower, self.lower_inclusive),
                (self.upper, self.upper_inclusive),
            ):
                _require(
                    (bound is None) == (inclusive is None),
                    "each existing bound requires explicit inclusivity",
                )
            if self.lower is None or self.upper is None:
                _require(
                    self.open_bound_basis is not None,
                    "open range requires a documented basis",
                )
        else:
            _require(
                all(
                    value is None
                    for value in (
                        self.lower,
                        self.upper,
                        self.lower_inclusive,
                        self.upper_inclusive,
                        self.open_bound_basis,
                    )
                ),
                "non-range selector cannot have range fields",
            )
            _require(
                (self.value is None) == (self.kind is SelectorKind.UNKNOWN),
                "exact/release-line requires value; unknown forbids value",
            )


class AssertionKind(StrEnum):
    BEHAVIOR = "behavior"
    TRANSITION = "transition"


@dataclass(frozen=True, kw_only=True)
class ApplicabilityAssertion(Record):
    kind: AssertionKind
    content_locator: str
    basis_locator: str
    basis: str
    basis_source_id: str | None = None
    applies_to: tuple[VersionSelector, ...] = ()
    transition_source: tuple[VersionSelector, ...] = ()
    transition_target: tuple[VersionSelector, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.kind is AssertionKind.BEHAVIOR:
            _require(bool(self.applies_to), "behavior requires applicability")
            _require(
                not self.transition_source and not self.transition_target,
                "behavior cannot have transition endpoints",
            )
        else:
            _require(not self.applies_to, "transition cannot have applies_to")
            _require(
                bool(self.transition_source) and bool(self.transition_target),
                "transition requires both endpoints",
            )


class DocumentType(StrEnum):
    REFERENCE = "reference"
    CONCEPTUAL_GUIDE = "conceptual_guide"
    MIGRATION_GUIDE = "migration_guide"
    RELEASE_NOTE = "release_note"
    DOCUMENTATION_EXAMPLE = "documentation_example"


class ContributionRole(StrEnum):
    PRIMARY_EXPLANATION = "primary_explanation"
    SUPPORTING_EXPLANATION = "supporting_explanation"
    COMPANION_EXAMPLE = "companion_example"


@dataclass(frozen=True, kw_only=True)
class SourceContribution(Record):
    """Map a frozen source span to a half-open character span in evidence.content."""

    source_id: str
    source_locator: str
    role: ContributionRole
    content_start: int
    content_end: int

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(
            0 <= self.content_start < self.content_end,
            "contribution requires a nonempty, nonnegative content span",
        )


@dataclass(frozen=True, kw_only=True)
class SourceManifestEntry(Record):
    source_id: str
    ecosystem_id: str
    document_type: DocumentType
    title: str
    canonical_url: str
    snapshot_locator: str
    content_hash: str
    document_version: VersionSelector
    captured_at: datetime
    publisher: str
    license: str
    transformation_record: str

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(
            self.captured_at.utcoffset() is not None,
            "captured_at must be timezone-aware",
        )
        _hash(self.content_hash)


def _hash(value: str) -> None:
    _require(
        value.startswith("sha256:")
        and len(value) == 71
        and all(c in "0123456789abcdef" for c in value[7:]),
        "content_hash must be sha256:<64 lowercase hex digits>",
    )


@dataclass(frozen=True, kw_only=True)
class EvidenceUnit(Record):
    evidence_id: str
    source_id: str
    ecosystem_id: str
    content: str
    content_hash: str
    section_path: tuple[str, ...]
    source_locator: str
    applicability: tuple[ApplicabilityAssertion, ...]
    technical_identifiers: tuple[str, ...] = ()
    curator_notes: str | None = None
    contributions: tuple[SourceContribution, ...] = ()
    assembly_policy: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(bool(self.section_path), "section_path must not be empty")
        _require(bool(self.applicability), "applicability must be explicit")
        _hash(self.content_hash)
        if self.contributions:
            _require(
                self.assembly_policy is not None,
                "explicit contributions require assembly_policy",
            )
            primary = [
                c
                for c in self.contributions
                if c.role is ContributionRole.PRIMARY_EXPLANATION
            ]
            _require(len(primary) == 1, "exactly one primary contribution required")
            _require(
                primary[0].source_id == self.source_id
                and primary[0].source_locator == self.source_locator,
                "primary contribution must match evidence source and locator",
            )
            end = 0
            for contribution in sorted(
                self.contributions, key=lambda c: c.content_start
            ):
                _require(
                    contribution.content_start == end,
                    "contribution content spans must partition content "
                    "without gaps or overlaps",
                )
                end = contribution.content_end
            _require(
                end == len(self.content),
                "contribution content spans must cover exactly the evidence content",
            )
        else:
            _require(
                self.assembly_policy is None,
                "assembly_policy requires explicit contributions",
            )
        contributing_sources = {self.source_id} | {
            c.source_id for c in self.contributions
        }
        for assertion in self.applicability:
            if self.contributions:
                _require(
                    assertion.basis_source_id is not None,
                    "explicit contributions require a source-qualified "
                    "applicability basis",
                )
            _require(
                (assertion.basis_source_id or self.source_id) in contributing_sources,
                "applicability basis must reference a contributing source",
            )


class QueryKind(StrEnum):
    LOOKUP = "lookup"
    MIGRATION = "migration"


class QueryCategory(StrEnum):
    EXACT_IDENTIFIER = "exact_identifier"
    NATURAL_LANGUAGE_MIGRATION = "natural_language_migration"
    NO_SUPPORTED_EVIDENCE = "no_supported_evidence"


class Answerability(StrEnum):
    ANSWERABLE = "answerable"
    UNANSWERABLE = "unanswerable"


@dataclass(frozen=True, kw_only=True)
class BenchmarkQuery(Record):
    query_id: str
    ecosystem_id: str
    query_text: str
    query_kind: QueryKind
    requested_version: VersionSelector
    primary_category: QueryCategory
    answerability: Answerability
    answerability_reason: str
    source_version: VersionSelector | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(
            self.requested_version.kind is SelectorKind.EXACT,
            "v0 queries require exact requested versions",
        )
        if self.query_kind is QueryKind.MIGRATION:
            _require(
                self.source_version is not None, "migration requires source_version"
            )
        else:
            _require(self.source_version is None, "lookup must not have source_version")
        if self.source_version is not None:
            _require(
                self.source_version.kind is SelectorKind.EXACT,
                "v0 queries require exact source versions",
            )
            _require(
                self.source_version.scheme == self.requested_version.scheme,
                "query endpoints must use the same version scheme",
            )


class VersionApplicability(StrEnum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class EvidenceRole(StrEnum):
    REQUESTED_BEHAVIOR = "requested_behavior"
    SOURCE_BEHAVIOR = "source_behavior"
    TARGET_BEHAVIOR = "target_behavior"
    TRANSITION = "transition"
    BACKGROUND = "background"


class ReviewStatus(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    ADJUDICATED = "adjudicated"


@dataclass(frozen=True, kw_only=True)
class GoldJudgment(Record):
    query_id: str
    evidence_id: str
    topical_relevance: int
    version_applicability: VersionApplicability
    evidence_roles: tuple[EvidenceRole, ...]
    rationale: str
    supporting_locators: tuple[str, ...]
    review_status: ReviewStatus
    hard_negative: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(self.topical_relevance in (0, 1, 2), "relevance must be 0, 1, or 2")
        _require(bool(self.evidence_roles), "judgment requires an evidence role")
        _require(bool(self.supporting_locators), "judgment requires source locators")
        _require(
            len(set(self.evidence_roles)) == len(self.evidence_roles),
            "duplicate evidence roles",
        )
        if self.hard_negative:
            _require(
                self.topical_relevance == 2
                and self.version_applicability is VersionApplicability.INVALID,
                "hard negative must be directly relevant and version-invalid",
            )

    @property
    def is_valid_positive(self) -> bool:
        return (
            self.review_status is not ReviewStatus.DRAFT
            and self.topical_relevance == 2
            and self.version_applicability is VersionApplicability.VALID
        )


@dataclass(frozen=True, kw_only=True)
class Benchmark(Record):
    """A complete, reviewed benchmark revision suitable for scoring."""

    benchmark_revision: str
    sources: tuple[SourceManifestEntry, ...]
    evidence: tuple[EvidenceUnit, ...]
    queries: tuple[BenchmarkQuery, ...]
    judgments: tuple[GoldJudgment, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _require(
            bool(self.sources) and bool(self.evidence) and bool(self.queries),
            "benchmark sources, evidence, and queries must not be empty",
        )
        _unique(tuple(s.source_id for s in self.sources), "source IDs")
        _unique(tuple(e.evidence_id for e in self.evidence), "evidence IDs")
        _unique(tuple(q.query_id for q in self.queries), "query IDs")
        sources = {s.source_id: s for s in self.sources}
        evidence = {e.evidence_id: e for e in self.evidence}
        queries = {q.query_id: q for q in self.queries}
        for unit in self.evidence:
            _require(unit.source_id in sources, "unknown evidence source_id")
            _require(
                unit.ecosystem_id == sources[unit.source_id].ecosystem_id,
                "evidence/source ecosystem mismatch",
            )
            for contribution in unit.contributions:
                _require(
                    contribution.source_id in sources, "unknown contribution source_id"
                )
                _require(
                    unit.ecosystem_id == sources[contribution.source_id].ecosystem_id,
                    "contribution/source ecosystem mismatch",
                )
        pairs: set[tuple[str, str]] = set()
        positives: set[str] = set()
        for judgment in self.judgments:
            _require(judgment.query_id in queries, "unknown judgment query_id")
            _require(judgment.evidence_id in evidence, "unknown judgment evidence_id")
            pair = (judgment.query_id, judgment.evidence_id)
            _require(pair not in pairs, "duplicate judgment pair")
            pairs.add(pair)
            _require(
                judgment.review_status is not ReviewStatus.DRAFT,
                "draft judgments cannot enter a scored benchmark",
            )
            if judgment.is_valid_positive:
                _require(
                    queries[judgment.query_id].ecosystem_id
                    == evidence[judgment.evidence_id].ecosystem_id,
                    "positive judgment ecosystem mismatch",
                )
                positives.add(judgment.query_id)
        _require(
            len(pairs) == len(queries) * len(evidence),
            "benchmark requires a complete query-evidence judgment matrix",
        )
        for query in self.queries:
            _require(
                (query.query_id in positives)
                == (query.answerability is Answerability.ANSWERABLE),
                f"{query.query_id}: answerability conflicts with valid positives",
            )


def _unique(values: tuple[str, ...], label: str) -> None:
    _require(len(set(values)) == len(values), f"duplicate {label}")


@dataclass(frozen=True, kw_only=True)
class RankedResult(Record):
    query_id: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _unique(self.evidence_ids, "ranked evidence IDs")


@dataclass(frozen=True, kw_only=True)
class RankedRun(Record):
    run_id: str
    benchmark_revision: str
    method_description: str
    results: tuple[RankedResult, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        _unique(tuple(result.query_id for result in self.results), "run query IDs")

    def validate_against(self, benchmark: Benchmark) -> None:
        _require(
            self.benchmark_revision == benchmark.benchmark_revision,
            "run benchmark revision mismatch",
        )
        _require(
            {r.query_id for r in self.results}
            == {q.query_id for q in benchmark.queries},
            "run must contain exactly the benchmark queries",
        )
        known = {unit.evidence_id for unit in benchmark.evidence}
        for result in self.results:
            _require(set(result.evidence_ids) <= known, "unknown run evidence ID")
