"""Positive applicability-aware reranking with pending experimental metadata only."""

import argparse
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import (
    ApplicabilityAssertion,
    AssertionKind,
    QueryKind,
    RankedResult,
    SelectorKind,
    VersionSelector,
)
from version_aware_retriever.hybrid import SourcePin, decode, source_rankings
from version_aware_retriever.lexical import (
    RetrievalQuery,
    canonical,
    documents_from_artifact,
    queries_from_public,
)

EVIDENCE = "data/pydantic/extraction/derived/evidence.json"
QUERIES = "data/pydantic/benchmark/queries.dev.input.json"
OUTPUT = "data/pydantic/runs/version-aware-rrf.dev.unscored.json"
SOURCE = SourcePin(
    "rrf-hybrid",
    "data/pydantic/runs/rrf-hybrid.dev.unscored.json",
    "rrf-hybrid:41875fdf7c4dc51de7870b2e690cb260c7e76ed8561a8cf11756c6db8cc97572",
    "sha256:d11ae6443840554bcf355fdee8e942b527e9f04c81d942357776ee8c7c0784f2",
)


class Classification(StrEnum):
    DIRECT_MATCH = "DIRECT_MATCH"
    TRANSITION_RELEVANT = "TRANSITION_RELEVANT"
    TRANSITION_MATCH = "TRANSITION_MATCH"
    SOURCE_AND_TARGET_MATCH = "SOURCE_AND_TARGET_MATCH"
    SOURCE_MATCH = "SOURCE_MATCH"
    TARGET_MATCH = "TARGET_MATCH"
    UNKNOWN = "UNKNOWN"


LOOKUP_TIERS = {
    Classification.DIRECT_MATCH: 1,
    Classification.TRANSITION_RELEVANT: 2,
    Classification.UNKNOWN: 3,
}
MIGRATION_TIERS = {
    Classification.TRANSITION_MATCH: 1,
    Classification.SOURCE_AND_TARGET_MATCH: 2,
    Classification.SOURCE_MATCH: 3,
    Classification.TARGET_MATCH: 3,
    Classification.UNKNOWN: 4,
}
POLICY = {
    "identifier": "positive-exact-applicability-rrf-v1",
    "metadata_status": "pending human review; experimental ranking metadata",
    "selector_policy": (
        "exact scheme and literal value equality only; other selectors unknown"
    ),
    "lookup_tiers": LOOKUP_TIERS,
    "migration_tiers": MIGRATION_TIERS,
    "return_policy": (
        "all source RRF results; tier ascending then original RRF rank ascending"
    ),
    "score_usage": (
        "preserved original RRF scores for diagnostics only; no scalar boost"
    ),
    "scope": (
        "matches assertion scopes, not query-specific topical relevance "
        "or whole-unit validity"
    ),
}


@dataclass(frozen=True)
class Match:
    assertion_index: int
    content_locator: str
    roles: tuple[str, ...]


@dataclass(frozen=True)
class Relation:
    classification: Classification
    tier: int
    matched_assertions: tuple[Match, ...]


def exact_match(selector: VersionSelector, requested: VersionSelector) -> bool:
    selector.__post_init__()
    requested.__post_init__()
    return (
        selector.kind is SelectorKind.EXACT
        and requested.kind is SelectorKind.EXACT
        and selector.scheme == requested.scheme
        and selector.value == requested.value
    )


def classify(
    assertions: tuple[ApplicabilityAssertion, ...], query: RetrievalQuery
) -> Relation:
    """Classify EvidenceUnit.applicability, without text/filename/gold inference."""
    query.__post_init__()
    matches = []
    roles_found: set[str] = set()
    for i, assertion in enumerate(assertions):
        assertion.__post_init__()
        roles = []
        if assertion.kind is AssertionKind.BEHAVIOR:
            if any(
                exact_match(v, query.requested_version) for v in assertion.applies_to
            ):
                roles.append(
                    "requested" if query.query_kind is QueryKind.LOOKUP else "target"
                )
            if query.source_version is not None and any(
                exact_match(v, query.source_version) for v in assertion.applies_to
            ):
                roles.append("source")
        elif query.query_kind is QueryKind.LOOKUP:
            for role, endpoints in (
                ("transition_source", assertion.transition_source),
                ("transition_target", assertion.transition_target),
            ):
                if any(exact_match(v, query.requested_version) for v in endpoints):
                    roles.append(role)
        elif query.source_version is not None:
            if any(
                exact_match(v, query.source_version)
                for v in assertion.transition_source
            ) and any(
                exact_match(v, query.requested_version)
                for v in assertion.transition_target
            ):
                roles.append("transition")
        if roles:
            matches.append(Match(i, assertion.content_locator, tuple(roles)))
            roles_found.update(roles)
    classification = Classification.UNKNOWN
    if query.query_kind is QueryKind.LOOKUP:
        if "requested" in roles_found:
            classification = Classification.DIRECT_MATCH
        elif roles_found & {"transition_source", "transition_target"}:
            classification = Classification.TRANSITION_RELEVANT
        tiers = LOOKUP_TIERS
    else:
        if "transition" in roles_found:
            classification = Classification.TRANSITION_MATCH
        elif {"source", "target"} <= roles_found:
            classification = Classification.SOURCE_AND_TARGET_MATCH
        elif "source" in roles_found:
            classification = Classification.SOURCE_MATCH
        elif "target" in roles_found:
            classification = Classification.TARGET_MATCH
        tiers = MIGRATION_TIERS
    return Relation(classification, tiers[classification], tuple(matches))


def decode_assertion(data: dict[str, Any]) -> ApplicabilityAssertion:
    def selectors(name: str) -> tuple[VersionSelector, ...]:
        return tuple(
            VersionSelector(**{**v, "kind": SelectorKind(v["kind"])})
            for v in data.get(name, [])
        )

    return ApplicabilityAssertion(
        **{
            **data,
            "kind": AssertionKind(data["kind"]),
            **{
                key: selectors(key)
                for key in ("applies_to", "transition_source", "transition_target")
            },
        }
    )


def rerank(
    query: RetrievalQuery,
    ranking: tuple[str, ...],
    metadata: Mapping[str, tuple[ApplicabilityAssertion, ...]],
) -> tuple[tuple[str, Relation, int], ...]:
    RankedResult(query_id=query.query_id, evidence_ids=ranking)
    require(set(ranking) <= metadata.keys(), "unknown ranking evidence ID")
    rows = [
        (eid, classify(metadata[eid], query), rank)
        for rank, eid in enumerate(ranking, 1)
    ]
    return tuple(sorted(rows, key=lambda row: (row[1].tier, row[2])))


def run_development(root: Path, *, source: SourcePin = SOURCE) -> dict[str, Any]:
    """Read only evidence/public inputs and frozen RRF; never load review or gold."""
    paths = (root / EVIDENCE, root / QUERIES, root / source.path)
    output = root / OUTPUT
    require(len({p.resolve() for p in (*paths, output)}) == 4, "overlapping paths")
    evidence_bytes, query_bytes, source_bytes = (p.read_bytes() for p in paths)
    artifact = decode(evidence_bytes)
    documents = sorted(documents_from_artifact(artifact), key=lambda d: d.evidence_id)
    queries = queries_from_public(decode(query_bytes))
    ids = {d.evidence_id for d in documents}
    require(
        len(documents) == len(ids) == 34 and len(queries) == 8,
        "expected 34 units/eight queries",
    )
    require(
        all(q.ecosystem_id in {d.ecosystem_id for d in documents} for q in queries),
        "query ecosystem absent",
    )
    metadata = {
        u["record"]["evidence_id"]: tuple(
            decode_assertion(a) for a in u["record"].get("applicability", [])
        )
        for u in artifact["units"]
    }
    snapshot = (
        "retrieval-input:"
        + digest(
            canonical(
                {
                    "documents": [asdict(d) for d in documents],
                    "queries": [asdict(q) for q in queries],
                }
            )
        )[7:]
    )
    hashes = {"evidence": digest(evidence_bytes), "public_queries": digest(query_bytes)}
    source_rows = source_rankings(
        source_bytes, source, snapshot, hashes, {q.query_id for q in queries}, ids
    )
    require(
        all(set(row) == ids for row in source_rows.values()),
        "RRF must retain all 34 units",
    )
    source_data = decode(source_bytes)
    source_scores = {r["query_id"]: r["scores"] for r in source_data["diagnostics"]}
    results, diagnostics = [], []
    for query in queries:
        rows = rerank(query, source_rows[query.query_id], metadata)
        results.append(
            asdict(
                RankedResult(
                    query_id=query.query_id, evidence_ids=tuple(row[0] for row in rows)
                )
            )
        )
        scores = source_scores[query.query_id]
        diagnostics.append(
            {
                "query_id": query.query_id,
                "scores": [scores[rank - 1] for _, _, rank in rows],
                "items": [
                    {
                        "evidence_id": eid,
                        "original_rrf_rank": rank,
                        "reranked_position": pos,
                        "original_rrf_score": scores[rank - 1],
                        **asdict(relation),
                    }
                    for pos, (eid, relation, rank) in enumerate(rows, 1)
                ],
                "tier_counts": {
                    str(tier): sum(r.tier == tier for _, r, _ in rows)
                    for tier in sorted(
                        set(
                            (
                                LOOKUP_TIERS
                                if query.query_kind is QueryKind.LOOKUP
                                else MIGRATION_TIERS
                            ).values()
                        )
                    )
                },
            }
        )
    provenance = {"run_id": source.run_id, "content_hash": digest(source_bytes)}
    report = {
        "format_version": 1,
        "status": "unscored",
        "run_id": "version-aware-rrf:"
        + digest(
            canonical({"source": provenance, "inputs": hashes, "configuration": POLICY})
        )[7:],
        "source_rrf": provenance,
        "retrieval_input_snapshot": snapshot,
        "artifact_hashes": hashes,
        "configuration": POLICY,
        "run_depth": len(ids),
        "results": results,
        "diagnostics": diagnostics,
    }
    body = (
        json.dumps(
            report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode()
    require(
        not any(p.is_symlink() for p in (output, *output.parents)), "output symlink"
    )
    if not output.exists() or output.read_bytes() != body:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(body)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    report = run_development(args.root)
    print(f"{report['run_id']}: eight queries; pending experimental metadata; unscored")


if __name__ == "__main__":
    main()
