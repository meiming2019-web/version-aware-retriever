"""Fixed, content-only BM25 baseline; no judgments or version-aware ranking."""

import argparse
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import (
    QueryKind,
    RankedResult,
    Record,
    SelectorKind,
    VersionSelector,
)

QUERY_FIELDS = (
    "query_id",
    "ecosystem_id",
    "query_text",
    "query_kind",
    "source_version",
    "requested_version",
)
CONFIG = {
    "algorithm": "bm25-positive-log-idf-v1",
    "formula": (
        "sum_unique_terms ln(1+(N-df+0.5)/(df+0.5))*tf*(k1+1)/(tf+k1*(1-b+b*dl/avgdl))"
    ),
    "tokenizer": "casefold-unicode-word-underscores-v1",
    "query_terms": "sorted distinct tokens",
    "k1": 1.2,
    "b": 0.75,
    "return_policy": (
        "all positive scores, descending unrounded score; "
        "evidence_id ascending on exact ties"
    ),
}


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\w+", text.casefold()))


@dataclass(frozen=True)
class Document:
    evidence_id: str
    ecosystem_id: str
    content: str

    def __post_init__(self) -> None:
        for value in (self.evidence_id, self.ecosystem_id):
            require(
                isinstance(value, str)
                and bool(value)
                and not any(c.isspace() for c in value),
                "invalid document ID",
            )
        require(isinstance(self.content, str), "content must be text")


@dataclass(frozen=True, kw_only=True)
class RetrievalQuery(Record):
    query_id: str
    ecosystem_id: str
    query_text: str
    query_kind: QueryKind
    source_version: VersionSelector | None
    requested_version: VersionSelector

    def __post_init__(self) -> None:
        super().__post_init__()
        require(
            self.requested_version.kind is SelectorKind.EXACT,
            "requested version must be exact",
        )
        require(
            (self.source_version is not None)
            == (self.query_kind is QueryKind.MIGRATION),
            "migration source version mismatch",
        )
        if self.source_version is not None:
            require(
                self.source_version.kind is SelectorKind.EXACT, "source must be exact"
            )
            require(
                self.source_version.scheme == self.requested_version.scheme,
                "version schemes differ",
            )


@dataclass(frozen=True)
class SearchHit:
    evidence_id: str
    score: float


class BM25Index:
    def __init__(self, documents: tuple[Document, ...]) -> None:
        require(
            len({d.evidence_id for d in documents}) == len(documents),
            "duplicate document IDs",
        )
        self.documents = tuple(sorted(documents, key=lambda d: d.evidence_id))
        self._terms = tuple(Counter(tokenize(d.content)) for d in self.documents)
        self._lengths = tuple(sum(t.values()) for t in self._terms)
        self._average = sum(self._lengths) / len(documents) if documents else 0.0
        self._df: Counter[str] = Counter()
        for terms in self._terms:
            self._df.update(terms.keys())

    def search(self, text: str, k: int | None = None) -> tuple[SearchHit, ...]:
        """Search all supplied documents; structured versions are not features."""
        require(
            k is None or (type(k) is int and k >= 0),
            "k must be a nonnegative integer or None",
        )
        if not self._average or k == 0:
            return ()
        query_terms = sorted(set(tokenize(text)) & self._df.keys())
        hits = []
        for doc, terms, length in zip(
            self.documents, self._terms, self._lengths, strict=True
        ):
            score = math.fsum(
                math.log1p(
                    (len(self.documents) - self._df[t] + 0.5) / (self._df[t] + 0.5)
                )
                * terms[t]
                * 2.2
                / (terms[t] + 1.2 * (1 - 0.75 + 0.75 * length / self._average))
                for t in query_terms
                if terms[t]
            )
            require(math.isfinite(score), "nonfinite BM25 score")
            if score > 0:
                hits.append(SearchHit(doc.evidence_id, score))
        hits.sort(key=lambda h: (-h.score, h.evidence_id))
        return tuple(hits if k is None else hits[:k])


def project_queries(draft: dict[str, Any]) -> list[dict[str, Any]]:
    """Mechanical one-time projection; never access an entry's curation object."""
    projected = []
    for entry in draft["queries"]:
        public = entry["retriever_input"]
        require(set(QUERY_FIELDS) <= public.keys(), "missing retrieval query field")
        projected.append({key: public[key] for key in QUERY_FIELDS})
    return projected


def documents_from_artifact(data: dict[str, Any]) -> tuple[Document, ...]:
    documents = []
    for unit in data["units"]:
        record = unit["record"]
        require(
            {"evidence_id", "ecosystem_id", "content"} <= record.keys(),
            "missing document field",
        )
        documents.append(
            Document(record["evidence_id"], record["ecosystem_id"], record["content"])
        )
    return tuple(documents)


def queries_from_public(data: list[dict[str, Any]]) -> tuple[RetrievalQuery, ...]:
    queries = []
    for row in data:
        require(
            set(row) == set(QUERY_FIELDS), "public query fields must match allowlist"
        )

        def version(value: dict[str, Any]) -> VersionSelector:
            return VersionSelector(**{**value, "kind": SelectorKind(value["kind"])})

        queries.append(
            RetrievalQuery(
                query_id=row["query_id"],
                ecosystem_id=row["ecosystem_id"],
                query_text=row["query_text"],
                query_kind=QueryKind(row["query_kind"]),
                source_version=version(row["source_version"])
                if row["source_version"] is not None
                else None,
                requested_version=version(row["requested_version"]),
            )
        )
    require(len({q.query_id for q in queries}) == len(queries), "duplicate query IDs")
    return tuple(queries)


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode()


def run_development(
    evidence: Path, public_queries: Path, output: Path, *, expected_queries: int = 8
) -> dict[str, Any]:
    """Read only the specified evidence/public inputs; never load authoring drafts."""
    require(
        output.resolve() not in (evidence.resolve(), public_queries.resolve()),
        "output overlaps input",
    )
    evidence_bytes, query_bytes = evidence.read_bytes(), public_queries.read_bytes()
    documents = documents_from_artifact(json.loads(evidence_bytes))
    queries = queries_from_public(json.loads(query_bytes))
    require(len(queries) == expected_queries, "unexpected query batch size")
    ecosystems = {d.ecosystem_id for d in documents}
    require(
        all(q.ecosystem_id in ecosystems for q in queries),
        "query ecosystem absent from corpus",
    )
    index = BM25Index(documents)
    snapshot = "retrieval-input:" + digest(
        canonical(
            {
                "documents": [asdict(d) for d in index.documents],
                "queries": [asdict(q) for q in queries],
            }
        )
    ).removeprefix("sha256:")
    results, diagnostics = [], []
    for query in queries:
        hits = index.search(query.query_text)
        result = RankedResult(
            query_id=query.query_id, evidence_ids=tuple(h.evidence_id for h in hits)
        )
        require(
            set(result.evidence_ids) <= {d.evidence_id for d in documents},
            "unknown result evidence",
        )
        results.append(asdict(result))
        diagnostics.append(
            {"query_id": query.query_id, "scores": [h.score for h in hits]}
        )
    require(
        {r["query_id"] for r in results} == {q.query_id for q in queries},
        "incomplete query results",
    )
    report = {
        "format_version": 1,
        "status": "unscored",
        "run_id": "bm25:"
        + digest(canonical({"snapshot": snapshot, "config": CONFIG})).removeprefix(
            "sha256:"
        ),
        "retrieval_input_snapshot": snapshot,
        "artifact_hashes": {
            "evidence": digest(evidence_bytes),
            "public_queries": digest(query_bytes),
        },
        "configuration": CONFIG,
        "run_depth": len(documents),
        "results": results,
        "diagnostics": diagnostics,
    }
    encoded = (
        json.dumps(
            report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode()
    require(not output.is_symlink(), "output must not be a symlink")
    if not output.exists() or output.read_bytes() != encoded:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encoded)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path("data/pydantic/extraction/derived/evidence.json"),
    )
    parser.add_argument(
        "--queries",
        type=Path,
        default=Path("data/pydantic/benchmark/queries.dev.input.json"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/pydantic/runs/bm25.dev.unscored.json")
    )
    args = parser.parse_args()
    report = run_development(args.evidence, args.queries, args.output)
    print(f"{report['run_id']}: {len(report['results'])} queries, unscored")


if __name__ == "__main__":
    main()
