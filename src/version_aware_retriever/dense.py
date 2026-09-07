"""Fixed development-only dense baseline. Preparation is the only online command."""

import argparse
import importlib
import importlib.metadata
import json
import math
import platform
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from version_aware_retriever.acquisition import digest, require
from version_aware_retriever.contracts import RankedResult
from version_aware_retriever.lexical import (
    SearchHit,
    canonical,
    documents_from_artifact,
    queries_from_public,
)

MODEL = "Alibaba-NLP/gte-modernbert-base"
REVISION = "e7f32e3c00f91d699e8c43b53106206bcc72bb22"
CONFIG = {
    "model": MODEL,
    "model_revision": REVISION,
    "tokenizer_revision": REVISION,
    "device": "cpu",
    "dtype": "float32",
    "batch_size": 4,
    "pooling": "published CLS; include_prompt=True",
    "prompts": {},
    "input_limit": 8192,
    "normalization": "ST L2; float64 L2 and dot for scoring",
    "preprocessing": "published ST Transformer; no custom prompts",
    "attention": "sdpa",
    "trust_remote_code": False,
    "weights": "safetensors",
    "return_policy": "all scores descending, exact ties ascending evidence_id",
}
FILES = [
    "README.md",
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "1_Pooling/config.json",
    "model.safetensors",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
]
Vector = tuple[float, ...]


def normalize(vector: Vector) -> Vector:
    require(bool(vector) and all(math.isfinite(x) for x in vector), "invalid vector")
    norm = math.hypot(*vector)
    require(math.isfinite(norm) and norm > 0, "zero or invalid norm")
    return tuple(x / norm for x in vector)


class VectorIndex:
    """Vectors align positionally with explicit IDs; never silently reorder rows."""

    def __init__(self, ids: tuple[str, ...], vectors: tuple[Vector, ...]) -> None:
        require(len(ids) == len(vectors), "ID/vector count mismatch")
        require(len(set(ids)) == len(ids), "duplicate IDs")
        require(all(x and not any(c.isspace() for c in x) for x in ids), "invalid ID")
        self.ids = ids
        self.vectors = tuple(normalize(v) for v in vectors)
        require(len({len(v) for v in vectors}) <= 1, "dimension mismatch")

    def search(self, vector: Vector, k: int | None = None) -> tuple[SearchHit, ...]:
        require(k is None or (type(k) is int and k >= 0), "invalid top-k")
        query = normalize(vector)
        if self.vectors:
            require(len(query) == len(self.vectors[0]), "dimension mismatch")
        hits = [
            SearchHit(key, math.fsum(a * b for a, b in zip(query, v, strict=True)))
            for key, v in zip(self.ids, self.vectors, strict=True)
        ]
        hits.sort(key=lambda h: (-h.score, h.evidence_id))
        return tuple(hits if k is None else hits[:k])


class Encoder(Protocol):
    def lengths(self, texts: list[str]) -> list[int]: ...
    def encode(self, texts: list[str]) -> tuple[Vector, ...]: ...


def snapshot(*, online: bool = False) -> Path:
    try:
        hub = importlib.import_module("huggingface_hub")
    except ImportError as exc:
        raise ValueError(
            "Install the optional dependencies with pip install -e '.[dense]'"
        ) from exc
    try:
        path = Path(
            hub.snapshot_download(
                MODEL,
                revision=REVISION,
                allow_patterns=FILES,
                local_files_only=not online,
            )
        )
        require(all((path / f).is_file() for f in FILES), "incomplete model snapshot")
        return path
    except (OSError, ValueError) as exc:
        raise ValueError(
            "Model unavailable: run python -m version_aware_retriever.dense prepare"
        ) from exc


class SentenceEncoder:
    def __init__(self) -> None:
        path = snapshot()
        torch = importlib.import_module("torch")
        st = importlib.import_module("sentence_transformers")
        self.model: Any = st.SentenceTransformer(
            str(path),
            device="cpu",
            trust_remote_code=False,
            local_files_only=True,
            model_kwargs={
                "torch_dtype": torch.float32,
                "use_safetensors": True,
                "attn_implementation": "sdpa",
            },
            tokenizer_kwargs={"local_files_only": True},
        )
        self.model.float().eval()
        pool = self.model[1].get_config_dict()
        require(
            pool["pooling_mode_cls_token"]
            and not any(
                value
                for key, value in pool.items()
                if key.startswith("pooling_mode_") and key != "pooling_mode_cls_token"
            ),
            "unexpected pooling",
        )
        require(
            not self.model.prompts and self.model.default_prompt_name is None,
            "unexpected prompts",
        )
        require(
            pool["include_prompt"] and not self.model[0].do_lower_case,
            "unexpected preprocessing",
        )
        require(self.model.max_seq_length == 8192, "unexpected input limit")

    def lengths(self, texts: list[str]) -> list[int]:
        # ST's published Transformer strips surrounding whitespace before tokenizing.
        tokens = self.model.tokenizer(
            [t.strip() for t in texts],
            truncation=False,
            padding=False,
            add_special_tokens=True,
        )["input_ids"]
        return [len(row) for row in tokens]

    def encode(self, texts: list[str]) -> tuple[Vector, ...]:
        torch = importlib.import_module("torch")
        with torch.inference_mode():
            array = self.model.encode(
                texts,
                batch_size=4,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        return tuple(tuple(float(x) for x in row) for row in array)


def embedding_pass(
    encoder: Encoder, ids: tuple[str, ...], texts: list[str]
) -> tuple[tuple[Vector, ...], list[int]]:
    require(len(ids) == len(texts) and len(set(ids)) == len(ids), "invalid input IDs")
    if not texts:
        return (), []
    lengths = encoder.lengths(texts)
    require(len(lengths) == len(ids), "token count mismatch")
    for key, length in zip(ids, lengths, strict=True):
        require(
            type(length) is int and 0 < length <= 8192,
            f"{key}: token length {length} exceeds input limit or is invalid",
        )
    vectors = encoder.encode(texts)
    VectorIndex(ids, vectors)
    return vectors, lengths


def write_json(path: Path, value: object) -> None:
    require(not path.is_symlink(), "output symlink")
    content = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if not path.exists() or path.read_text() != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def load_cache(path: Path, binding: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_bytes())
    require(data["binding"] == binding, "stale embedding cache")
    payload = {k: data[k] for k in ("binding", "vectors", "lengths")}
    require(data["identity"] == digest(canonical(payload)), "cache hash mismatch")
    ids = tuple(binding["ids"])
    VectorIndex(ids, tuple(tuple(v) for v in data["vectors"]))
    require(len(data["lengths"]) == len(ids), "cache token count mismatch")
    require(
        all(type(n) is int and 0 < n <= 8192 for n in data["lengths"]),
        "invalid cached token lengths",
    )
    return data


def run_development(
    evidence: Path,
    public_queries: Path,
    output: Path,
    cache: Path,
    *,
    fresh: bool = False,
    encoder: Encoder | None = None,
    expected_queries: int = 8,
) -> dict[str, Any]:
    require(
        len({p.resolve() for p in (evidence, public_queries, output, cache)}) == 4,
        "overlapping paths",
    )
    evidence_bytes, query_bytes = evidence.read_bytes(), public_queries.read_bytes()
    documents = tuple(
        sorted(
            documents_from_artifact(json.loads(evidence_bytes)),
            key=lambda d: d.evidence_id,
        )
    )
    queries = queries_from_public(json.loads(query_bytes))
    require(
        len(documents) == 34 and len(queries) == expected_queries,
        "unexpected document/query count",
    )
    require(
        all(q.ecosystem_id in {d.ecosystem_id for d in documents} for q in queries),
        "query ecosystem absent",
    )
    texts = [d.content for d in documents] + [q.query_text for q in queries]
    ids = tuple(d.evidence_id for d in documents) + tuple(q.query_id for q in queries)
    projected = {
        "documents": [asdict(d) for d in documents],
        "queries": [asdict(q) for q in queries],
    }
    input_snapshot = "retrieval-input:" + digest(canonical(projected))[7:]
    versions = {}
    for package in (
        "sentence-transformers",
        "transformers",
        "torch",
        "numpy",
        "tokenizers",
        "huggingface-hub",
        "safetensors",
    ):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    binding = {
        "ids": list(ids),
        "texts_hash": digest(canonical(texts)),
        "configuration": CONFIG,
        "packages": versions,
    }
    reused = cache.exists() and not fresh
    if reused:
        artifact = load_cache(cache, binding)
    else:
        vectors, lengths = embedding_pass(encoder or SentenceEncoder(), ids, texts)
        artifact = {"binding": binding, "vectors": vectors, "lengths": lengths}
        artifact["identity"] = digest(canonical(artifact))
        write_json(cache, artifact)
    vectors = tuple(tuple(v) for v in artifact["vectors"])
    index = VectorIndex(ids[:34], vectors[:34])
    results, diagnostics = [], []
    for query, vector in zip(queries, vectors[34:], strict=True):
        hits = index.search(vector) if query.query_text.strip() else ()
        results.append(
            asdict(
                RankedResult(
                    query_id=query.query_id,
                    evidence_ids=tuple(h.evidence_id for h in hits),
                )
            )
        )
        diagnostics.append(
            {"query_id": query.query_id, "scores": [h.score for h in hits]}
        )
    report = {
        "status": "unscored",
        "format_version": 1,
        "run_id": "dense:"
        + digest(
            canonical(
                {
                    "input": input_snapshot,
                    "embedding": artifact["identity"],
                    "configuration": CONFIG,
                }
            )
        )[7:],
        "retrieval_input_snapshot": input_snapshot,
        "artifact_hashes": {
            "evidence": digest(evidence_bytes),
            "public_queries": digest(query_bytes),
        },
        "configuration": CONFIG,
        "embedding_identity": artifact["identity"],
        "runtime": {
            "packages": versions,
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "length_checks": {
            "max_document": max(artifact["lengths"][:34]),
            "max_query": max(artifact["lengths"][34:]),
            "truncations": 0,
        },
        "vector_shapes": [[34, len(vectors[0])], [len(queries), len(vectors[0])]],
        "run_depth": 34,
        "results": results,
        "diagnostics": diagnostics,
    }
    write_json(output, report)
    print("reused embeddings" if reused else "fresh encoding")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument(
        "--cache", type=Path, default=Path(".dense-cache/embeddings.json")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/pydantic/runs/dense.dev.unscored.json"),
    )
    args = parser.parse_args()
    if args.command == "prepare":
        print(snapshot(online=True))
    else:
        run_development(
            Path("data/pydantic/extraction/derived/evidence.json"),
            Path("data/pydantic/benchmark/queries.dev.input.json"),
            args.output,
            args.cache,
            fresh=args.fresh,
        )


if __name__ == "__main__":
    main()
