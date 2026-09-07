"""Fixed local cross-encoder over frozen RRF top 20; preparation alone is online."""

import argparse
import importlib
import importlib.metadata
import json
import math
import platform
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import RankedResult
from version_aware_retriever.hybrid import SourcePin, decode, source_rankings
from version_aware_retriever.lexical import (
    canonical,
    documents_from_artifact,
    queries_from_public,
)

MODEL = "BAAI/bge-reranker-v2-m3"
REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"
EVIDENCE = "data/pydantic/extraction/derived/evidence.json"
QUERIES = "data/pydantic/benchmark/queries.dev.input.json"
MANIFEST = "data/pydantic/frozen/manifest.json"
OUTPUT = "data/pydantic/runs/cross-encoder-reranked.dev.unscored.json"
SOURCE = SourcePin(
    "rrf-hybrid",
    "data/pydantic/runs/rrf-hybrid.dev.unscored.json",
    "rrf-hybrid:41875fdf7c4dc51de7870b2e690cb260c7e76ed8561a8cf11756c6db8cc97572",
    "sha256:d11ae6443840554bcf355fdee8e942b527e9f04c81d942357776ee8c7c0784f2",
)
FILES = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "special_tokens_map.json",
    "model.safetensors",
    "README.md",
)
CONFIG = {
    "model": MODEL,
    "model_revision": REVISION,
    "tokenizer_revision": REVISION,
    "device": "cpu",
    "dtype": "float32",
    "batch_size": 4,
    "trust_remote_code": False,
    "weights": "safetensors",
    "attention": "sdpa",
    "candidate_depth": 20,
    "input_limit": 8192,
    "truncation": False,
    "header_policy": "primary-source snapshot ecosystem/release and document type v1",
    "query_policy": "unaltered public query_text; no prompt",
    "return_policy": "RRF top 20 only; descending raw logit, original RRF rank, ID",
}


class PairScorer(Protocol):
    def lengths(self, pairs: list[tuple[str, str]]) -> list[int]: ...
    def score(self, pairs: list[tuple[str, str]]) -> list[float]: ...


def snapshot(*, online: bool = False) -> Path:
    try:
        hub = importlib.import_module("huggingface_hub")
        path = Path(
            hub.snapshot_download(
                MODEL,
                revision=REVISION,
                allow_patterns=list(FILES),
                local_files_only=not online,
            )
        )
        require(
            all((path / name).is_file() for name in FILES), "incomplete model cache"
        )
        return path
    except (ImportError, OSError, ValueError) as exc:
        raise ValueError(
            "Install .[reranker], then run python -m "
            "version_aware_retriever.reranker prepare with network access; "
            "run never downloads or substitutes a model"
        ) from exc


class LocalScorer:
    def __init__(self) -> None:
        path = snapshot()
        transformers = importlib.import_module("transformers")
        self.torch = importlib.import_module("torch")
        self.torch.set_num_threads(4)
        self.torch.use_deterministic_algorithms(True)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
            path,
            local_files_only=True,
            trust_remote_code=False,
            use_fast=True,
        )
        config = transformers.AutoConfig.from_pretrained(
            path,
            local_files_only=True,
            trust_remote_code=False,
        )
        require(
            config.architectures == ["XLMRobertaForSequenceClassification"]
            and config.num_labels == 1
            and config.pad_token_id == 1
            and config.max_position_embeddings == 8194
            and self.tokenizer.model_max_length == 8192,
            "unexpected model architecture or effective input limit",
        )
        # XLM-R nonpad position IDs start at padding_idx + 1: 8194 - 1 - 1.
        self.path = path
        self.model: Any = None
        self.runtime = {
            "python": platform.python_version(),
            "platform": platform.system(),
            "machine": platform.machine(),
            "threads": 4,
            "packages": {
                p: importlib.metadata.version(p)
                for p in (
                    "torch",
                    "transformers",
                    "huggingface-hub",
                    "tokenizers",
                    "safetensors",
                )
            },
        }

    def lengths(self, pairs: list[tuple[str, str]]) -> list[int]:
        return [
            len(ids)
            for ids in self.tokenizer(
                pairs,
                padding=False,
                truncation=False,
                add_special_tokens=True,
            )["input_ids"]
        ]

    def score(self, pairs: list[tuple[str, str]]) -> list[float]:
        transformers = importlib.import_module("transformers")
        self.model = (
            transformers.AutoModelForSequenceClassification.from_pretrained(
                self.path,
                local_files_only=True,
                trust_remote_code=False,
                use_safetensors=True,
                torch_dtype=self.torch.float32,
                attn_implementation="sdpa",
            )
            .to("cpu")
            .eval()
        )
        scores = []
        with self.torch.inference_mode():
            for start in range(0, len(pairs), 4):
                inputs = self.tokenizer(
                    pairs[start : start + 4],
                    padding=True,
                    truncation=False,
                    add_special_tokens=True,
                    return_tensors="pt",
                )
                scores.extend(self.model(**inputs).logits.view(-1).float().tolist())
                print(f"scored {min(start + 4, len(pairs))}/{len(pairs)}", flush=True)
        return scores


def passage(record: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    require(record["source_id"] in sources, "missing primary source")
    source = sources[record["source_id"]]
    require(source["ecosystem_id"] == record["ecosystem_id"], "ecosystem mismatch")
    version = source["document_version"]
    require(
        version["kind"] == "exact" and bool(version["value"]), "exact snapshot required"
    )
    project = source["ecosystem_id"]
    # Display the registered project name; no behavior inference.
    project = "Pydantic" if project == "pypi:pydantic" else project
    return (
        f"[Document snapshot: {project} {version['value']}]\n"
        f"[Document type: {source['document_type']}]\n\n{record['content']}"
    )


def top20(ranking: tuple[str, ...], known: set[str]) -> tuple[str, ...]:
    RankedResult(query_id="candidate-input", evidence_ids=ranking)
    require(all(e and not any(c.isspace() for c in e) for e in ranking), "invalid ID")
    require(set(ranking) <= known, "missing document IDs")
    require(len(ranking) >= 20, "requires 20 candidates")
    return ranking[:20]


def rerank(
    query_id: str, candidates: tuple[str, ...], scores: list[float]
) -> tuple[str, ...]:
    RankedResult(query_id=query_id, evidence_ids=candidates)
    require(bool(candidates), "empty candidates")
    require(
        all(e and not any(c.isspace() for c in e) for e in candidates), "invalid ID"
    )
    require(len(scores) == len(candidates), "score-count mismatch")
    require(
        all(type(s) in (int, float) and math.isfinite(s) for s in scores),
        "nonfinite score",
    )
    return tuple(
        candidates[i]
        for i in sorted(
            range(len(candidates)),
            key=lambda i: (-scores[i], i, candidates[i]),
        )
    )


def run_development(
    root: Path,
    scorer: PairScorer,
    runtime: dict[str, Any],
    *,
    source: SourcePin = SOURCE,
    public_queries: str = QUERIES,
    output_path: str = OUTPUT,
    expected_queries: int = 8,
) -> dict[str, Any]:
    paths = [root / p for p in (EVIDENCE, public_queries, MANIFEST, source.path)]
    output = root / output_path
    require(len({p.resolve() for p in (*paths, output)}) == 5, "overlapping paths")
    eb, qb, mb, rb = [p.read_bytes() for p in paths]
    artifact = decode(eb)
    documents = sorted(documents_from_artifact(artifact), key=lambda d: d.evidence_id)
    queries = queries_from_public(decode(qb))
    known = {d.evidence_id for d in documents}
    require(
        len(known) == 34 and len(queries) == expected_queries,
        "unexpected unit/query count",
    )
    snapshot_id = (
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
    hashes = {"evidence": digest(eb), "public_queries": digest(qb)}
    rankings = source_rankings(
        rb, source, snapshot_id, hashes, {q.query_id for q in queries}, known
    )
    source_list = [s["record"] for s in decode(mb)["sources"]]
    sources = {s["source_id"]: s for s in source_list}
    require(len(sources) == len(source_list), "duplicate sources")
    passages = {
        u["record"]["evidence_id"]: passage(u["record"], sources)
        for u in artifact["units"]
    }
    candidates = {q.query_id: top20(rankings[q.query_id], known) for q in queries}
    pairs = [
        (q.query_text, passages[e]) for q in queries for e in candidates[q.query_id]
    ]
    lengths = scorer.lengths(pairs)
    require(
        len(lengths) == expected_queries * 20
        and all(type(n) is int and n > 0 for n in lengths),
        "invalid lengths",
    )
    oversized = [
        {
            "query_id": q.query_id,
            "evidence_id": e,
            "length": lengths[i * 20 + j],
            "limit": 8192,
        }
        for i, q in enumerate(queries)
        for j, e in enumerate(candidates[q.query_id])
        if lengths[i * 20 + j] > 8192
    ]
    require(not oversized, f"input length blocker; no scoring: {oversized}")
    scores = scorer.score(pairs)
    require(len(scores) == expected_queries * 20, "score-count mismatch")
    results, diagnostics = [], []
    for i, q in enumerate(queries):
        ids = candidates[q.query_id]
        values = scores[i * 20 : (i + 1) * 20]
        ordered = rerank(q.query_id, ids, values)
        positions = {e: j for j, e in enumerate(ids)}
        results.append({"query_id": q.query_id, "evidence_ids": ordered})
        diagnostics.append(
            {
                "query_id": q.query_id,
                "scores": [values[positions[e]] for e in ordered],
                "original_rrf_ranks": [positions[e] + 1 for e in ordered],
                "pair_lengths": [lengths[i * 20 + positions[e]] for e in ordered],
            }
        )
    report = {
        "format_version": 1,
        "status": "unscored",
        "run_depth": 20,
        "source_rrf": {"run_id": source.run_id, "content_hash": digest(rb)},
        "retrieval_input_snapshot": snapshot_id,
        "artifact_hashes": hashes,
        "manifest_hash": digest(mb),
        "configuration": CONFIG,
        "runtime": runtime,
        "input_lengths": {
            "limit": 8192,
            "maximum": max(lengths),
            "minimum": min(lengths),
            "sorted_lengths": sorted(lengths),
            "truncation_count": 0,
        },
        "results": results,
        "diagnostics": diagnostics,
    }
    report["run_id"] = "cross-encoder:" + digest(canonical(report))[7:]
    body = (
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
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
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.command == "prepare":
        print(snapshot(online=True))
        return
    start = time.perf_counter()
    scorer = LocalScorer()
    report = run_development(args.root, scorer, scorer.runtime)
    print(
        f"{report['run_id']}; 160 pairs; CPU elapsed {time.perf_counter() - start:.3f}s"
    )


if __name__ == "__main__":
    main()
