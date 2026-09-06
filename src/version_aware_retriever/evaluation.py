"""Deterministic scoring of accepted results against reviewed, fixed judgments."""

from dataclasses import dataclass
from math import fsum

from version_aware_retriever.contracts import (
    Answerability,
    Benchmark,
    RankedRun,
    VersionApplicability,
)

CUTOFFS = (1, 3, 5)


@dataclass(frozen=True)
class QueryCutoff:
    k: int
    hits: int
    recall: float | None
    returned_count: int
    wrong_version_count: int
    unknown_count: int


@dataclass(frozen=True)
class QueryReport:
    query_id: str
    answerability: Answerability
    gold_positive_count: int
    accepted_count: int
    first_positive_rank: int | None
    reciprocal_rank: float | None
    unanswerable_false_positive: bool | None
    cutoffs: tuple[QueryCutoff, ...]


@dataclass(frozen=True)
class CutoffReport:
    k: int
    recall: float | None
    wrong_version_rate: float | None
    wrong_version_count: int
    returned_count: int
    unknown_count: int


@dataclass(frozen=True)
class EvaluationReport:
    benchmark_revision: str
    run_id: str
    cutoffs: tuple[int, ...]
    query_count: int
    answerable_count: int
    unanswerable_count: int
    accepted_item_count: int
    empty_result_count: int
    unanswerable_false_positive_count: int
    mrr: float | None
    unanswerable_false_positive_rate: float | None
    at_cutoffs: tuple[CutoffReport, ...]
    queries: tuple[QueryReport, ...]


def evaluate(benchmark: Benchmark, run: RankedRun) -> EvaluationReport:
    """Score without mutation or label inference; raise ContractError on bad inputs.

    Records already validate at construction. Recheck gold, benchmark coverage,
    ranked-result uniqueness and run compatibility at this scoring boundary.
    """
    for judgment in benchmark.judgments:
        judgment.__post_init__()
    benchmark.__post_init__()
    run.__post_init__()
    for result in run.results:
        result.__post_init__()
    run.validate_against(benchmark)

    gold = {q.query_id: set[str]() for q in benchmark.queries}
    judgments = {(j.query_id, j.evidence_id): j for j in benchmark.judgments}
    for judgment in benchmark.judgments:
        if judgment.is_valid_positive:
            gold[judgment.query_id].add(judgment.evidence_id)
    results = {r.query_id: r.evidence_ids for r in run.results}
    reports: list[QueryReport] = []
    for query in benchmark.queries:
        accepted = results[query.query_id]
        positives = gold[query.query_id]
        answerable = query.answerability is Answerability.ANSWERABLE
        rank = next((i for i, eid in enumerate(accepted, 1) if eid in positives), None)
        cutoff_reports: list[QueryCutoff] = []
        for k in CUTOFFS:
            returned = accepted[:k]
            hits = len(set(returned) & positives)
            labels = [judgments[query.query_id, eid] for eid in returned]
            cutoff_reports.append(
                QueryCutoff(
                    k=k,
                    hits=hits,
                    recall=hits / len(positives) if answerable else None,
                    returned_count=len(returned),
                    wrong_version_count=sum(
                        j.topical_relevance == 2
                        and j.version_applicability is VersionApplicability.INVALID
                        for j in labels
                    ),
                    unknown_count=sum(
                        j.version_applicability is VersionApplicability.UNKNOWN
                        for j in labels
                    ),
                )
            )
        reports.append(
            QueryReport(
                query_id=query.query_id,
                answerability=query.answerability,
                gold_positive_count=len(positives),
                accepted_count=len(accepted),
                first_positive_rank=rank,
                reciprocal_rank=(1 / rank if rank else 0.0) if answerable else None,
                unanswerable_false_positive=None if answerable else bool(accepted),
                cutoffs=tuple(cutoff_reports),
            )
        )
    answerable_count = sum(q.answerability is Answerability.ANSWERABLE for q in reports)
    unanswerable_count = len(reports) - answerable_count
    false_positives = sum(q.unanswerable_false_positive is True for q in reports)
    aggregates: list[CutoffReport] = []
    for i, k in enumerate(CUTOFFS):
        entries = [q.cutoffs[i] for q in reports]
        returned_count = sum(c.returned_count for c in entries)
        wrong_count = sum(c.wrong_version_count for c in entries)
        aggregates.append(
            CutoffReport(
                k=k,
                recall=(
                    fsum(c.recall for c in entries if c.recall is not None)
                    / answerable_count
                    if answerable_count
                    else None
                ),
                wrong_version_rate=wrong_count / returned_count
                if returned_count
                else None,
                wrong_version_count=wrong_count,
                returned_count=returned_count,
                unknown_count=sum(c.unknown_count for c in entries),
            )
        )
    return EvaluationReport(
        benchmark_revision=benchmark.benchmark_revision,
        run_id=run.run_id,
        cutoffs=CUTOFFS,
        query_count=len(reports),
        answerable_count=answerable_count,
        unanswerable_count=unanswerable_count,
        accepted_item_count=sum(q.accepted_count for q in reports),
        empty_result_count=sum(q.accepted_count == 0 for q in reports),
        unanswerable_false_positive_count=false_positives,
        mrr=(
            fsum(q.reciprocal_rank for q in reports if q.reciprocal_rank is not None)
            / answerable_count
            if answerable_count
            else None
        ),
        unanswerable_false_positive_rate=(
            false_positives / unanswerable_count if unanswerable_count else None
        ),
        at_cutoffs=tuple(aggregates),
        queries=tuple(reports),
    )
