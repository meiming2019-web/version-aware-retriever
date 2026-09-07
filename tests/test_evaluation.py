"""Fictional test-only gold; reviewed statuses do not describe real annotations."""

import copy
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
from version_aware_retriever.evaluation import evaluate


@pytest.fixture
def benchmark() -> Benchmark:
    version = VersionSelector(kind=SelectorKind.EXACT, scheme="fictional", value="r2")
    text = "Fictional scoring fixture, not real benchmark evidence."
    digest = "sha256:" + sha256(text.encode()).hexdigest()
    source = SourceManifestEntry(
        source_id="fictional-source",
        ecosystem_id="fictional:widget",
        document_type=DocumentType.REFERENCE,
        title="Test-only",
        canonical_url="https://example.invalid/test",
        snapshot_locator="fixture:r2",
        content_hash=digest,
        document_version=version,
        captured_at=datetime(2026, 1, 1, tzinfo=UTC),
        publisher="Fictional",
        license="Test only",
        transformation_record="None",
    )
    evidence = tuple(
        EvidenceUnit(
            evidence_id=f"E{i}",
            source_id=source.source_id,
            ecosystem_id=source.ecosystem_id,
            content=text,
            content_hash=digest,
            section_path=("Test",),
            source_locator="fixture:1",
            applicability=(
                ApplicabilityAssertion(
                    kind=AssertionKind.BEHAVIOR,
                    content_locator="fixture:1",
                    basis_locator="fixture:1",
                    basis="Fictional assumption",
                    applies_to=(version,),
                ),
            ),
        )
        for i in range(1, 7)
    )
    queries = tuple(
        BenchmarkQuery(
            query_id=q,
            ecosystem_id=source.ecosystem_id,
            query_text=f"Fictional question {q}?",
            query_kind=QueryKind.LOOKUP,
            requested_version=version,
            primary_category=QueryCategory.EXACT_IDENTIFIER,
            answerability=Answerability.UNANSWERABLE
            if q == "U"
            else Answerability.ANSWERABLE,
            answerability_reason="Hand-assigned synthetic fixture only",
        )
        for q in ("A", "B", "U")
    )
    judgments = []
    for q in queries:
        for e in evidence:
            positive = (q.query_id, e.evidence_id) in {
                ("A", "E1"),
                ("A", "E2"),
                ("B", "E4"),
            }
            wrong = q.query_id in ("A", "U") and e.evidence_id == "E3"
            unknown_direct = q.query_id == "A" and e.evidence_id == "E6"
            judgments.append(
                GoldJudgment(
                    query_id=q.query_id,
                    evidence_id=e.evidence_id,
                    topical_relevance=2 if positive or wrong or unknown_direct else 0,
                    version_applicability=(
                        VersionApplicability.VALID
                        if positive
                        else VersionApplicability.INVALID
                        if wrong or e.evidence_id == "E5"
                        else VersionApplicability.UNKNOWN
                    ),
                    evidence_roles=(EvidenceRole.REQUESTED_BEHAVIOR,),
                    rationale="Hand-assigned test-only judgment",
                    supporting_locators=("fixture:1",),
                    review_status=ReviewStatus.ADJUDICATED
                    if e.evidence_id == "E2"
                    else ReviewStatus.REVIEWED,
                    # False even for wrong E3: scoring uses labels, not this hint.
                    hard_negative=False,
                )
            )
    return Benchmark(
        benchmark_revision="fictional-v0",
        sources=(source,),
        evidence=evidence,
        queries=queries,
        judgments=tuple(judgments),
    )


def run_for(
    b: Benchmark,
    a: tuple[str, ...] = (),
    b_items: tuple[str, ...] = (),
    u: tuple[str, ...] = (),
) -> RankedRun:
    items = {"A": a, "B": b_items, "U": u}
    return RankedRun(
        run_id="fictional-run",
        benchmark_revision=b.benchmark_revision,
        method_description="Hand-ranked test only",
        results=tuple(
            RankedResult(query_id=q.query_id, evidence_ids=items[q.query_id])
            for q in b.queries
        ),
    )


def test_hand_worked_example(benchmark: Benchmark) -> None:
    report = evaluate(benchmark, run_for(benchmark, ("E3", "E1"), ("E4",)))
    # A: 1/2 gold at rank 2. B: 1/1 at rank 1. U abstains.
    # Recall@3 = (.5 + 1)/2; MRR = (.5 + 1)/2; wrong = 1/(2+1).
    assert report.cutoffs == (1, 3, 5)
    assert report.at_cutoffs[0].recall == 0.5
    assert report.at_cutoffs[0].wrong_version_rate == 0.5
    assert report.at_cutoffs[1].recall == 0.75
    assert report.mrr == 0.75
    assert report.at_cutoffs[1].wrong_version_rate == pytest.approx(1 / 3)
    assert report.at_cutoffs[1].wrong_version_count == 1
    assert report.at_cutoffs[1].returned_count == 3
    assert report.unanswerable_false_positive_rate == 0
    assert report.queries[0].gold_positive_count == 2
    assert report.queries[0].cutoffs[1].hits == 1
    assert report.queries[0].cutoffs[1].recall == 0.5
    assert report.queries[0].first_positive_rank == 2
    assert report.queries[2].reciprocal_rank is None
    assert report.queries[2].cutoffs[1].recall is None
    assert (report.query_count, report.answerable_count, report.unanswerable_count) == (
        3,
        2,
        1,
    )
    assert (report.accepted_item_count, report.empty_result_count) == (3, 1)


def test_perfect_and_deterministic(benchmark: Benchmark) -> None:
    run = run_for(benchmark, ("E1", "E2"), ("E4",))
    before = copy.deepcopy((benchmark, run))
    report = evaluate(benchmark, run)
    assert report == evaluate(benchmark, run)
    assert (benchmark, run) == before
    assert report.mrr == 1
    assert report.at_cutoffs[0].recall == 0.75  # Recall is not Hit@1.
    assert report.at_cutoffs[1].recall == 1
    assert report.at_cutoffs[2].wrong_version_rate == 0
    assert report.benchmark_revision == benchmark.benchmark_revision
    assert report.run_id == run.run_id


def test_full_list_mrr_beyond_five(benchmark: Benchmark) -> None:
    report = evaluate(
        benchmark, run_for(benchmark, (), ("E1", "E2", "E3", "E5", "E6", "E4"))
    )
    assert report.queries[1].first_positive_rank == 6
    assert report.queries[1].reciprocal_rank == pytest.approx(1 / 6)
    assert report.mrr == pytest.approx(1 / 12)
    assert report.at_cutoffs[2].recall == 0
    assert report.accepted_item_count == 6


def test_all_empty(benchmark: Benchmark) -> None:
    report = evaluate(benchmark, run_for(benchmark))
    assert report.mrr == 0
    assert report.unanswerable_false_positive_rate == 0
    assert report.empty_result_count == 3
    for c in report.at_cutoffs:
        assert c.recall == 0
        assert c.wrong_version_rate is None
        assert c.returned_count == c.wrong_version_count == c.unknown_count == 0


@pytest.mark.parametrize("item", ["E1", "E3", "E5", "E6"])
def test_any_acceptance_on_unanswerable(benchmark: Benchmark, item: str) -> None:
    report = evaluate(benchmark, run_for(benchmark, u=(item,)))
    assert report.unanswerable_false_positive_rate == 1
    assert report.unanswerable_false_positive_count == 1
    assert report.queries[2].unanswerable_false_positive is True
    assert report.at_cutoffs[0].wrong_version_count == (1 if item == "E3" else 0)


def test_unknown_and_unrelated_invalid(benchmark: Benchmark) -> None:
    report = evaluate(benchmark, run_for(benchmark, ("E5", "E6")))
    assert report.mrr == 0
    assert report.at_cutoffs[1].recall == 0
    assert report.at_cutoffs[1].unknown_count == 1
    assert report.queries[0].cutoffs[1].unknown_count == 1
    assert report.at_cutoffs[1].wrong_version_rate == 0
    assert report.at_cutoffs[1].returned_count == 2


@pytest.mark.parametrize("only_unanswerable", [True, False])
def test_absent_query_class(benchmark: Benchmark, only_unanswerable: bool) -> None:
    queries = tuple(
        q for q in benchmark.queries if (q.query_id == "U") == only_unanswerable
    )
    ids = {q.query_id for q in queries}
    b = replace(
        benchmark,
        queries=queries,
        judgments=tuple(j for j in benchmark.judgments if j.query_id in ids),
    )
    report = evaluate(b, run_for(b))
    if only_unanswerable:
        assert report.mrr is None
        assert all(c.recall is None for c in report.at_cutoffs)
        assert report.unanswerable_false_positive_rate == 0
    else:
        assert report.mrr == 0
        assert report.unanswerable_false_positive_rate is None


@pytest.mark.parametrize(
    "problem", ["draft", "coverage", "answerability", "duplicate", "unknown"]
)
def test_reject_bad_benchmark_at_scoring(benchmark: Benchmark, problem: str) -> None:
    # Deliberately bypass frozen construction to test the scoring boundary recheck.
    bad = copy.deepcopy(benchmark)
    if problem == "draft":
        object.__setattr__(
            bad,
            "judgments",
            (
                replace(bad.judgments[0], review_status=ReviewStatus.DRAFT),
                *bad.judgments[1:],
            ),
        )
    elif problem == "coverage":
        object.__setattr__(bad, "judgments", bad.judgments[:-1])
    elif problem == "answerability":
        object.__setattr__(
            bad,
            "queries",
            (
                replace(bad.queries[0], answerability=Answerability.UNANSWERABLE),
                *bad.queries[1:],
            ),
        )
    elif problem == "duplicate":
        object.__setattr__(bad, "evidence", (*bad.evidence, bad.evidence[0]))
    else:
        object.__setattr__(
            bad,
            "judgments",
            (replace(bad.judgments[0], evidence_id="missing"), *bad.judgments[1:]),
        )
    with pytest.raises(ContractError):
        evaluate(bad, run_for(benchmark))


@pytest.mark.parametrize(
    "problem",
    [
        "revision",
        "missing",
        "unexpected",
        "unknown",
        "duplicate_item",
        "duplicate_query",
    ],
)
def test_reject_bad_run(benchmark: Benchmark, problem: str) -> None:
    run = run_for(benchmark)
    if problem == "revision":
        run = replace(run, benchmark_revision="other")
    elif problem == "missing":
        run = replace(run, results=run.results[:-1])
    elif problem == "unexpected":
        run = replace(
            run, results=(*run.results, RankedResult(query_id="other", evidence_ids=()))
        )
    elif problem == "unknown":
        run = run_for(benchmark, ("missing",))
    elif problem == "duplicate_item":
        object.__setattr__(run.results[0], "evidence_ids", ("E1", "E1"))
    else:
        object.__setattr__(run, "results", (*run.results, run.results[0]))
    with pytest.raises(ContractError):
        evaluate(benchmark, run)
