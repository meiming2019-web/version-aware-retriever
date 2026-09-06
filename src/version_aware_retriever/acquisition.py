"""Narrow pinned-source acquisition; default verification is entirely offline."""

import argparse
import hashlib
import json
import os
import ssl
import tempfile
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from version_aware_retriever.contracts import (
    ContractError,
    DocumentType,
    Record,
    SelectorKind,
    SourceManifestEntry,
    VersionSelector,
)

REPOSITORY = "https://github.com/pydantic/pydantic"
PINS = {
    "1.10.13": "8822578619bf8d0bb754b1cf7a2a905b50240d01",
    "2.5.3": "9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4",
}
TRANSFORMATION = "none: original HTTP response bytes retained; no extraction"
Fetch = Callable[[str], bytes]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def source_id(repository: str, commit: str, path: str) -> str:
    """Identity v1: SHA-256 of the UTF-8 JSON array [repository, commit, path]."""
    key = json.dumps([repository, commit, path], separators=(",", ":"))
    return "source:" + hashlib.sha256(key.encode("utf-8")).hexdigest()


@dataclass(frozen=True, kw_only=True)
class SelectedSource(Record):
    repository: str
    release: str
    discovery_tag: str
    commit: str
    path: str
    document_type: DocumentType
    sections: tuple[str, ...]
    companion_of: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        require(self.repository == REPOSITORY, "unapproved repository")
        require(PINS.get(self.release) == self.commit, "unapproved pinned commit")
        require(self.discovery_tag == "v" + self.release, "discovery tag mismatch")
        path = PurePosixPath(self.path)
        require(
            not path.is_absolute()
            and ".." not in path.parts
            and str(path) == self.path
            and "\\" not in self.path,
            "unsafe source path",
        )
        require(bool(self.sections), "selection requires section boundaries")

    @property
    def identity(self) -> str:
        return source_id(self.repository, self.commit, self.path)

    @property
    def retained_path(self) -> str:
        return f"sources/{self.commit}/{self.path}"


def read_selection(path: Path) -> tuple[SelectedSource, ...]:
    data = json.loads(path.read_bytes())
    require(data["selection_version"] == 1, "unsupported selection version")
    records = tuple(
        SelectedSource(
            **{
                **item,
                "document_type": DocumentType(item["document_type"]),
                "sections": tuple(item["sections"]),
            }
        )
        for item in data["sources"]
    )
    require(len(records) == 20, "approved selection requires 20 content files")
    require(len({s.identity for s in records}) == 20, "duplicate selection source")
    require(
        sum(s.document_type is DocumentType.DOCUMENTATION_EXAMPLE for s in records)
        == 11,
        "selection requires 11 example companions",
    )
    for item in records:
        if item.document_type is DocumentType.DOCUMENTATION_EXAMPLE:
            require(
                any(
                    s.commit == item.commit
                    and s.path == item.companion_of
                    and s.document_type is not DocumentType.DOCUMENTATION_EXAMPLE
                    for s in records
                ),
                "unknown companion parent",
            )
        else:
            require(item.companion_of is None, "primary document cannot be companion")
    return records


def raw_url(commit: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/pydantic/pydantic/{commit}/{path}"


def fetch_bytes(url: str, *, ca_file: str | None = None) -> bytes:
    context = ssl.create_default_context(cafile=ca_file)
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=60, context=context) as response:
        require(
            response.status == 200 and response.url == url,
            "source response must be HTTP 200 at the pinned URL",
        )
        body: bytes = response.read()
        length = response.headers.get("Content-Length")
        require(length is None or int(length) == len(body), "partial source response")
        require(bool(body), "empty source response")
        return body


def license_path(commit: str) -> str:
    return f"licenses/{commit}/LICENSE"


def record_for(
    item: SelectedSource, content_hash: str, captured_at: datetime
) -> SourceManifestEntry:
    return SourceManifestEntry(
        source_id=item.identity,
        ecosystem_id="pypi:pydantic",
        document_type=item.document_type,
        title=item.path,
        canonical_url=f"{item.repository}/blob/{item.commit}/{item.path}",
        snapshot_locator=raw_url(item.commit, item.path),
        content_hash=content_hash,
        document_version=VersionSelector(
            kind=SelectorKind.EXACT, scheme="pep440", value=item.release
        ),
        captured_at=captured_at,
        publisher="Pydantic project",
        license=f"MIT; basis: {license_path(item.commit)} (same pinned repository)",
        transformation_record=TRANSFORMATION,
    )


def record_json(record: SourceManifestEntry) -> dict[str, Any]:
    return {**asdict(record), "captured_at": record.captured_at.isoformat()}


def decode_record(data: dict[str, Any]) -> SourceManifestEntry:
    version = data["document_version"]
    return SourceManifestEntry(
        **{
            **data,
            "captured_at": datetime.fromisoformat(data["captured_at"]),
            "document_type": DocumentType(data["document_type"]),
            "document_version": VersionSelector(
                **{**version, "kind": SelectorKind(version["kind"])}
            ),
        }
    )


def verify(selection_path: Path, destination: Path) -> int:
    """Validate the complete source manifest and every retained byte, offline."""
    selected = {s.identity: s for s in read_selection(selection_path)}
    manifest = json.loads(checked_file(destination, "manifest.json"))
    require(manifest["format_version"] == 1, "unsupported manifest version")
    require(
        manifest["selection_hash"] == digest(selection_path.read_bytes()),
        "selection hash mismatch",
    )
    rows = manifest["sources"]
    require(len(rows) == len(selected), "manifest source count mismatch")
    seen: set[str] = set()
    expected_files = {"manifest.json"}
    for row in rows:
        record = decode_record(row["record"])
        require(record.source_id not in seen, "duplicate manifest source ID")
        seen.add(record.source_id)
        require(record.source_id in selected, "unexpected manifest source")
        item = selected[record.source_id]
        require(row["retained_path"] == item.retained_path, "retained path mismatch")
        expected_files.add(item.retained_path)
        require(
            row["release"] == item.release
            and row["discovery_tag"] == item.discovery_tag
            and row["commit"] == item.commit
            and row["path"] == item.path
            and row["repository"] == item.repository,
            "pinned snapshot mismatch",
        )
        body = checked_file(destination, item.retained_path)
        require(record.content_hash == digest(body), "retained-file hash mismatch")
        require(
            record == record_for(item, digest(body), record.captured_at),
            "source record provenance mismatch",
        )
    require(seen == set(selected), "missing manifest source")
    artifacts = manifest["licenses"]
    require(len(artifacts) == len(PINS), "license artifact count mismatch")
    seen_licenses: set[str] = set()
    for artifact in artifacts:
        commit = artifact["commit"]
        require(
            commit in PINS.values() and commit not in seen_licenses,
            "unexpected or duplicate license artifact",
        )
        seen_licenses.add(commit)
        path = license_path(commit)
        require(
            artifact["retained_path"] == path
            and artifact["url"] == raw_url(commit, "LICENSE"),
            "license provenance mismatch",
        )
        acquired = datetime.fromisoformat(artifact["captured_at"])
        require(acquired.utcoffset() is not None, "license timestamp requires timezone")
        body = checked_file(destination, path)
        require(artifact["content_hash"] == digest(body), "license hash mismatch")
        check_license(body)
        expected_files.add(path)
    actual_files = {
        p.relative_to(destination).as_posix()
        for p in destination.rglob("*")
        if p.is_file() or p.is_symlink()
    }
    require(actual_files == expected_files, "unexpected retained files")
    return len(seen)


def checked_file(root: Path, relative: str) -> bytes:
    path = root / relative
    require(
        not any(p.is_symlink() for p in (path, *path.parents)),
        "frozen paths must not be symlinks",
    )
    return path.read_bytes()


def check_license(body: bytes) -> None:
    require(
        b"Permission is hereby granted, free of charge" in body
        and b"copyright notice" in body.lower(),
        "expected MIT license notice missing",
    )


def acquire(selection_path: Path, destination: Path, fetch: Fetch = fetch_bytes) -> int:
    """Reuse only verified archives; publish a new archive only after all checks."""
    selected = read_selection(selection_path)
    if destination.exists():
        return verify(selection_path, destination)
    payloads: dict[str, bytes] = {}
    rows: list[dict[str, Any]] = []
    licenses: list[dict[str, str]] = []
    for item in selected:
        body = fetch(raw_url(item.commit, item.path))
        require(
            isinstance(body, bytes) and bool(body), "empty or invalid source response"
        )
        captured = datetime.now(UTC)
        payloads[item.retained_path] = body
        rows.append(
            {
                "record": record_json(record_for(item, digest(body), captured)),
                "retained_path": item.retained_path,
                "repository": item.repository,
                "release": item.release,
                "discovery_tag": item.discovery_tag,
                "commit": item.commit,
                "path": item.path,
            }
        )
    for commit in PINS.values():
        url = raw_url(commit, "LICENSE")
        body = fetch(url)
        check_license(body)
        path = license_path(commit)
        payloads[path] = body
        licenses.append(
            {
                "commit": commit,
                "url": url,
                "retained_path": path,
                "content_hash": digest(body),
                "captured_at": datetime.now(UTC).isoformat(),
            }
        )
    manifest = {
        "format_version": 1,
        "selection_hash": digest(selection_path.read_bytes()),
        "sources": rows,
        "licenses": licenses,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".freeze-", dir=destination.parent
    ) as temporary:
        stage = Path(temporary) / "snapshot"
        stage.mkdir()
        for relative, body in payloads.items():
            retained = stage / relative
            retained.parent.mkdir(parents=True, exist_ok=True)
            retained.write_bytes(body)
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        count = verify(selection_path, stage)
        require(not destination.exists(), "destination appeared during acquisition")
        os.rename(stage, destination)
    return count


def verify_online(
    selection_path: Path, destination: Path, fetch: Fetch = fetch_bytes
) -> int:
    count = verify(selection_path, destination)
    for item in read_selection(selection_path):
        require(
            fetch(raw_url(item.commit, item.path))
            == checked_file(destination, item.retained_path),
            "online source mismatch",
        )
    for commit in PINS.values():
        require(
            fetch(raw_url(commit, "LICENSE"))
            == checked_file(destination, license_path(commit)),
            "online license mismatch",
        )
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("acquire", "verify", "verify-online"))
    parser.add_argument(
        "--selection", type=Path, default=Path("data/pydantic/selection.json")
    )
    parser.add_argument(
        "--destination", type=Path, default=Path("data/pydantic/frozen")
    )
    parser.add_argument("--ca-file", help="Optional trusted CA bundle for HTTPS")
    args = parser.parse_args()

    def fetch(url: str) -> bytes:
        return fetch_bytes(url, ca_file=args.ca_file)

    if args.command == "verify":
        count = verify(args.selection, args.destination)
    elif args.command == "acquire":
        count = acquire(args.selection, args.destination, fetch)
    else:
        count = verify_online(args.selection, args.destination, fetch)
    print(
        f"{args.command}: verified {count}/20 content sources and 2 license artifacts"
    )


if __name__ == "__main__":
    main()
