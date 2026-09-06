"""Synthetic test-only records. These are not the real benchmark or source data."""

from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256

import pytest

from version_aware_retriever.contracts import (
    Answerability,
    ApplicabilityAssertion,
    AssertionKind,
    Benchmark,
    BenchmarkQuery,
    ContractError,
    DocumentType,
    EvidenceRole,
    EvidenceUnit,
    GoldJudgment,
    QueryCategory,
    QueryKind,
    RankedResult,
    RankedRun,
    ReviewStatus,
    SelectorKind,
    SourceManifestEntry,
    VersionApplicability,
    VersionSelector,
)


@pytest.fixture
def benchmark() -> Benchmark:
    """Two fictional releases, two evidence units, and two fully judged queries."""
    version = VersionSelector(kind=SelectorKind.EXACT, scheme="synthetic", value="r2")
    text = "Synthetic test-only behavior description."
    digest = "sha256:" + sha256(text.encode()).hexdigest()
    source = SourceManifestEntry(
        source_id="test-source",
        ecosystem_id="example:widget",
        document_type=DocumentType.REFERENCE,
        title="Test-only source",
        canonical_url="https://example.invalid/widget",
        snapshot_locator="fixture:r2",
        content_hash=digest,
        document_version=version,
        captured_at=datetime(2026, 1, 1, tzinfo=UTC),
        publisher="Fictional publisher",
        license="Test-only",
        transformation_record="Identity transformation",
    )
    unit = EvidenceUnit(
        evidence_id="test-new",
        source_id=source.source_id,
        ecosystem_id=source.ecosystem_id,
        content=text,
        content_hash=digest,
        section_path=("Behavior",),
        source_locator="#behavior",
        applicability=(
            ApplicabilityAssertion(
                kind=AssertionKind.BEHAVIOR,
                content_locator="#behavior",
                basis_locator="#behavior",
                basis="Explicit fictional release label",
                applies_to=(version,),
            ),
        ),
    )
    old = replace(
        unit,
        evidence_id="test-old",
        applicability=(
            replace(unit.applicability[0], applies_to=(replace(version, value="r1"),)),
        ),
    )
    query = BenchmarkQuery(
        query_id="test-answerable",
        ecosystem_id=source.ecosystem_id,
        query_text="What is the behavior in r2?",
        query_kind=QueryKind.LOOKUP,
        requested_version=version,
        primary_category=QueryCategory.EXACT_IDENTIFIER,
        answerability=Answerability.ANSWERABLE,
        answerability_reason="The fictional r2 unit directly supports this.",
    )
    absent = replace(
        query,
        query_id="test-absent",
        query_text="Is export supported?",
        primary_category=QueryCategory.NO_SUPPORTED_EVIDENCE,
        answerability=Answerability.UNANSWERABLE,
        answerability_reason="Neither test unit describes export.",
    )
    positive = GoldJudgment(
        query_id=query.query_id,
        evidence_id=unit.evidence_id,
        topical_relevance=2,
        version_applicability=VersionApplicability.VALID,
        evidence_roles=(EvidenceRole.REQUESTED_BEHAVIOR,),
        rationale="Explicit fictional r2 support",
        supporting_locators=("#behavior",),
        review_status=ReviewStatus.REVIEWED,
    )
    negative = replace(
        positive,
        evidence_id=old.evidence_id,
        version_applicability=VersionApplicability.INVALID,
        hard_negative=True,
        rationale="Same behavior topic, wrong release",
    )
    unrelated = tuple(
        replace(
            positive,
            query_id=absent.query_id,
            evidence_id=e.evidence_id,
            topical_relevance=0,
            version_applicability=VersionApplicability.UNKNOWN,
            evidence_roles=(EvidenceRole.BACKGROUND,),
            rationale="No export support in this unit",
        )
        for e in (unit, old)
    )
    return Benchmark(
        benchmark_revision="test-only-v0",
        sources=(source,),
        evidence=(unit, old),
        queries=(query, absent),
        judgments=(positive, negative, *unrelated),
    )


def run_for(benchmark: Benchmark) -> RankedRun:
    return RankedRun(
        run_id="test-run",
        benchmark_revision=benchmark.benchmark_revision,
        method_description="Manually constructed test-only run",
        results=(
            RankedResult(
                query_id=benchmark.queries[0].query_id,
                evidence_ids=(benchmark.evidence[0].evidence_id,),
            ),
            RankedResult(query_id=benchmark.queries[1].query_id, evidence_ids=()),
        ),
    )


def test_complete_benchmark_and_empty_abstention(benchmark: Benchmark) -> None:
    run_for(benchmark).validate_against(benchmark)
    assert benchmark.judgments[0].is_valid_positive
    assert not benchmark.judgments[1].is_valid_positive
    assert not benchmark.judgments[2].is_valid_positive


@pytest.mark.parametrize("field", ["sources", "evidence", "queries", "judgments"])
def test_duplicate_benchmark_records(benchmark: Benchmark, field: str) -> None:
    with pytest.raises(ContractError, match="duplicate"):
        if field == "sources":
            replace(benchmark, sources=(*benchmark.sources, benchmark.sources[0]))
        elif field == "evidence":
            replace(benchmark, evidence=(*benchmark.evidence, benchmark.evidence[0]))
        elif field == "queries":
            replace(benchmark, queries=(*benchmark.queries, benchmark.queries[0]))
        else:
            replace(benchmark, judgments=(*benchmark.judgments, benchmark.judgments[0]))


def test_unknown_source_and_ecosystem(benchmark: Benchmark) -> None:
    for changed in (
        replace(benchmark.evidence[0], source_id="missing"),
        replace(benchmark.evidence[0], ecosystem_id="other:project"),
    ):
        with pytest.raises(ContractError):
            replace(benchmark, evidence=(changed, benchmark.evidence[1]))


def test_unknown_judgment_references(benchmark: Benchmark) -> None:
    for changed in (
        replace(benchmark.judgments[0], query_id="missing"),
        replace(benchmark.judgments[0], evidence_id="missing"),
    ):
        with pytest.raises(ContractError, match="unknown judgment"):
            replace(benchmark, judgments=(changed, *benchmark.judgments[1:]))


def test_missing_judgment(benchmark: Benchmark) -> None:
    with pytest.raises(ContractError, match="complete"):
        replace(benchmark, judgments=benchmark.judgments[:-1])


def test_draft_never_counts_as_gold(benchmark: Benchmark) -> None:
    draft = replace(benchmark.judgments[0], review_status=ReviewStatus.DRAFT)
    assert not draft.is_valid_positive
    with pytest.raises(ContractError, match="draft"):
        replace(benchmark, judgments=(draft, *benchmark.judgments[1:]))


def test_adjudicated_positive(benchmark: Benchmark) -> None:
    positive = replace(benchmark.judgments[0], review_status=ReviewStatus.ADJUDICATED)
    replace(benchmark, judgments=(positive, *benchmark.judgments[1:]))
    assert positive.is_valid_positive


def test_answerability_requires_positive(benchmark: Benchmark) -> None:
    unknown = replace(
        benchmark.judgments[0], version_applicability=VersionApplicability.UNKNOWN
    )
    with pytest.raises(ContractError, match="answerability"):
        replace(benchmark, judgments=(unknown, *benchmark.judgments[1:]))
    absent = replace(benchmark.queries[0], answerability=Answerability.UNANSWERABLE)
    with pytest.raises(ContractError, match="answerability"):
        replace(benchmark, queries=(absent, benchmark.queries[1]))


def test_query_versions(benchmark: Benchmark) -> None:
    lookup = benchmark.queries[0]
    migration = replace(
        lookup,
        query_kind=QueryKind.MIGRATION,
        source_version=replace(lookup.requested_version, value="r1"),
    )
    assert migration.source_version is not None
    with pytest.raises(ContractError, match="source_version"):
        replace(migration, source_version=None)
    with pytest.raises(ContractError, match="lookup"):
        replace(lookup, source_version=lookup.requested_version)
    with pytest.raises(ContractError, match="requested_version"):
        replace(lookup, requested_version=None)  # type: ignore[arg-type]
    with pytest.raises(ContractError, match="exact requested"):
        replace(
            lookup,
            requested_version=VersionSelector(
                kind=SelectorKind.UNKNOWN, scheme="synthetic"
            ),
        )


def test_invalid_ids_and_runtime_types(benchmark: Benchmark) -> None:
    for identifier in ("", " ", "has space"):
        with pytest.raises(ContractError):
            replace(benchmark.queries[0], query_id=identifier)
    with pytest.raises(ContractError, match="invalid type"):
        replace(benchmark.queries[0], query_kind="lookup")  # type: ignore[arg-type]
    with pytest.raises(ContractError, match="invalid type"):
        replace(benchmark.judgments[0], topical_relevance=True)
    with pytest.raises(ContractError, match="invalid type"):
        replace(benchmark.evidence[0], applicability=[])  # type: ignore[arg-type]


def test_run_references(benchmark: Benchmark) -> None:
    run = run_for(benchmark)
    bad_runs = (
        replace(run, benchmark_revision="different"),
        replace(run, results=run.results[:1]),
        replace(
            run, results=(*run.results, RankedResult(query_id="extra", evidence_ids=()))
        ),
        replace(
            run,
            results=(
                replace(run.results[0], evidence_ids=("unknown",)),
                run.results[1],
            ),
        ),
    )
    for invalid in bad_runs:
        with pytest.raises(ContractError):
            invalid.validate_against(benchmark)
    with pytest.raises(ContractError, match="duplicate run query"):
        replace(run, results=(run.results[0], run.results[0]))
    with pytest.raises(ContractError, match="duplicate ranked"):
        replace(run.results[0], evidence_ids=("test-new", "test-new"))


def test_selectors() -> None:
    VersionSelector(kind=SelectorKind.RELEASE_LINE, scheme="calendar", value="2026")
    VersionSelector(kind=SelectorKind.UNKNOWN, scheme="calendar")
    VersionSelector(
        kind=SelectorKind.RANGE,
        scheme="calendar",
        lower="2025",
        upper="2026",
        lower_inclusive=True,
        upper_inclusive=False,
    )
    VersionSelector(
        kind=SelectorKind.RANGE,
        scheme="calendar",
        lower="2025",
        lower_inclusive=True,
        open_bound_basis="Explicit source assertion",
    )
    with pytest.raises(ContractError, match="basis"):
        VersionSelector(
            kind=SelectorKind.RANGE,
            scheme="calendar",
            lower="2025",
            lower_inclusive=True,
        )
    with pytest.raises(ContractError, match="inclusivity"):
        VersionSelector(kind=SelectorKind.RANGE, scheme="calendar", lower="2025")
    with pytest.raises(ContractError):
        VersionSelector(kind=SelectorKind.EXACT, scheme="calendar")
    with pytest.raises(ContractError):
        VersionSelector(kind=SelectorKind.UNKNOWN, scheme="calendar", value="2026")


def test_transition_and_hard_negative(benchmark: Benchmark) -> None:
    version = benchmark.queries[0].requested_version
    assertion = replace(
        benchmark.evidence[0].applicability[0],
        kind=AssertionKind.TRANSITION,
        applies_to=(),
        transition_source=(replace(version, value="r1"),),
        transition_target=(version,),
    )
    with pytest.raises(ContractError, match="both endpoints"):
        replace(assertion, transition_target=())
    with pytest.raises(ContractError, match="hard negative"):
        replace(benchmark.judgments[0], hard_negative=True)
    with pytest.raises(ContractError, match="applicability"):
        replace(benchmark.evidence[0], applicability=())


def test_provenance(benchmark: Benchmark) -> None:
    with pytest.raises(ContractError, match="timezone"):
        replace(benchmark.sources[0], captured_at=datetime(2026, 1, 1))
    with pytest.raises(ContractError, match="sha256"):
        replace(benchmark.sources[0], content_hash="not-a-hash")
    with pytest.raises(ContractError, match="blank"):
        replace(benchmark.judgments[0], rationale="")


def test_migration_source_and_transition_can_be_positives(benchmark: Benchmark) -> None:
    query = replace(
        benchmark.queries[0],
        query_kind=QueryKind.MIGRATION,
        source_version=replace(benchmark.queries[0].requested_version, value="r1"),
    )
    transition = replace(
        benchmark.judgments[0], evidence_roles=(EvidenceRole.TRANSITION,)
    )
    old_behavior = replace(
        benchmark.judgments[1],
        version_applicability=VersionApplicability.VALID,
        evidence_roles=(EvidenceRole.SOURCE_BEHAVIOR,),
        hard_negative=False,
    )
    validated = replace(
        benchmark,
        queries=(query, benchmark.queries[1]),
        judgments=(transition, old_behavior, *benchmark.judgments[2:]),
    )
    assert all(j.is_valid_positive for j in validated.judgments[:2])


def test_bad_retrieval_is_still_a_structurally_valid_run(benchmark: Benchmark) -> None:
    run = run_for(benchmark)
    replace(
        run,
        results=tuple(
            replace(result, evidence_ids=("test-old",)) for result in run.results
        ),
    ).validate_against(benchmark)


def test_cross_ecosystem_positive_rejected(benchmark: Benchmark) -> None:
    query = replace(benchmark.queries[0], ecosystem_id="another:project")
    with pytest.raises(ContractError, match="positive judgment ecosystem"):
        replace(benchmark, queries=(query, benchmark.queries[1]))
