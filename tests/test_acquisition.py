"""Offline acquisition tests using fictional bytes, never real benchmark evidence."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from version_aware_retriever.acquisition import (
    PINS,
    REPOSITORY,
    acquire,
    digest,
    fetch_bytes,
    read_selection,
    source_id,
    verify,
    verify_online,
)
from version_aware_retriever.contracts import ContractError

SELECTION = Path(__file__).resolve().parents[1] / "data/pydantic/selection.json"
SYNTHETIC = b"Test-only source\r\nUnicode: \xc3\xa9\r\n  trailing spaces  \n"
LICENSE = (
    b"Synthetic test-only license: Permission is hereby granted, free of charge\n"
    b"retain copyright notice\n"
)


def fake_fetch(url: str) -> bytes:
    return LICENSE if url.endswith("/LICENSE") else SYNTHETIC


@pytest.fixture
def frozen(tmp_path: Path) -> Path:
    destination = tmp_path / "frozen"
    assert acquire(SELECTION, destination, fake_fetch) == 20
    return destination


def manifest(root: Path) -> dict[str, Any]:
    result: dict[str, Any] = json.loads((root / "manifest.json").read_bytes())
    return result


def save_manifest(root: Path, data: dict[str, Any]) -> None:
    (root / "manifest.json").write_text(json.dumps(data), encoding="utf-8")


def test_identity_and_approved_selection() -> None:
    selected = read_selection(SELECTION)
    assert len(selected) == 20
    assert len({s.identity for s in selected}) == 20
    item = selected[0]
    assert item.identity == source_id(REPOSITORY, item.commit, item.path)
    assert item.identity != source_id(REPOSITORY, item.commit, "other.md")
    assert item.identity != source_id(REPOSITORY, PINS["2.5.3"], item.path)
    assert item.identity != source_id("https://example.invalid", item.commit, item.path)


def test_raw_preservation_and_repeat(frozen: Path) -> None:
    before = (frozen / "manifest.json").read_bytes()
    for row in manifest(frozen)["sources"]:
        assert (frozen / row["retained_path"]).read_bytes() == SYNTHETIC
        assert row["record"]["content_hash"] == digest(SYNTHETIC)

    def no_network(url: str) -> bytes:
        pytest.fail(f"repeat acquisition contacted {url}")

    assert acquire(SELECTION, frozen, no_network) == 20
    assert (frozen / "manifest.json").read_bytes() == before
    assert verify(SELECTION, frozen) == 20


@pytest.mark.parametrize("failure_at", [1, 10, 20, 22])
def test_partial_acquisition_not_published(tmp_path: Path, failure_at: int) -> None:
    calls = 0

    def failing(url: str) -> bytes:
        nonlocal calls
        calls += 1
        if calls == failure_at:
            raise OSError("synthetic failed response")
        return fake_fetch(url)

    destination = tmp_path / "frozen"
    with pytest.raises(OSError, match="failed response"):
        acquire(SELECTION, destination, failing)
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == []


def test_empty_response_not_published(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="empty"):
        acquire(SELECTION, tmp_path / "frozen", lambda url: b"")
    assert not (tmp_path / "frozen").exists()


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "duplicate", "unknown", "pin", "hash", "record"]
)
def test_bad_manifest_rejected(frozen: Path, mutation: str) -> None:
    data = manifest(frozen)
    if mutation == "missing":
        data["sources"].pop()
    elif mutation == "extra":
        data["sources"].append(data["sources"][0])
    elif mutation == "duplicate":
        data["sources"][1] = data["sources"][0]
    elif mutation == "unknown":
        data["sources"][0]["record"]["source_id"] = "unexpected"
    elif mutation == "pin":
        data["sources"][0]["commit"] = "main"
    elif mutation == "hash":
        data["sources"][0]["record"]["content_hash"] = "sha256:" + "0" * 64
    else:
        data["sources"][0]["record"]["publisher"] = ""
    save_manifest(frozen, data)
    with pytest.raises(ContractError):
        verify(SELECTION, frozen)


def test_corruption_not_overwritten(frozen: Path) -> None:
    path = frozen / manifest(frozen)["sources"][0]["retained_path"]
    path.write_bytes(b"synthetic corruption")
    with pytest.raises(ContractError, match="hash mismatch"):
        acquire(SELECTION, frozen, fake_fetch)
    assert path.read_bytes() == b"synthetic corruption"


def test_missing_file_rejected(frozen: Path) -> None:
    path = frozen / manifest(frozen)["sources"][0]["retained_path"]
    path.unlink()
    with pytest.raises(FileNotFoundError):
        acquire(SELECTION, frozen, fake_fetch)
    assert not path.exists()


def test_incomplete_existing_directory_rejected(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        acquire(SELECTION, tmp_path, fake_fetch)


def test_license_and_extra_file_validation(frozen: Path) -> None:
    path = frozen / "unexpected.txt"
    path.write_bytes(b"test-only")
    with pytest.raises(ContractError, match="unexpected retained"):
        verify(SELECTION, frozen)
    path.unlink()
    license_file = frozen / manifest(frozen)["licenses"][0]["retained_path"]
    license_file.write_bytes(b"bad notice")
    with pytest.raises(ContractError, match="license hash"):
        verify(SELECTION, frozen)


def test_selection_change_rejected(frozen: Path, tmp_path: Path) -> None:
    changed = tmp_path / "changed.json"
    changed.write_bytes(SELECTION.read_bytes() + b"\n")
    with pytest.raises(ContractError, match="selection hash"):
        verify(changed, frozen)


def test_optional_online_verification_is_mocked(frozen: Path) -> None:
    assert verify_online(SELECTION, frozen, fake_fetch) == 20
    with pytest.raises(ContractError, match="online source mismatch"):
        verify_online(SELECTION, frozen, lambda url: b"changed remote content")


@pytest.mark.parametrize("failure", ["status", "redirect", "partial", "empty"])
def test_http_response_rejection(monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    url = "https://example.invalid/test-only"
    response = MagicMock()
    response.__enter__.return_value = response
    response.status = 404 if failure == "status" else 200
    response.url = url + "/redirect" if failure == "redirect" else url
    response.read.return_value = b"" if failure == "empty" else SYNTHETIC
    response.headers = (
        {"Content-Length": str(len(SYNTHETIC) + 1)} if failure == "partial" else {}
    )
    monkeypatch.setattr("urllib.request.urlopen", MagicMock(return_value=response))
    with pytest.raises(ContractError):
        fetch_bytes(url)


def test_symlink_content_rejected(frozen: Path, tmp_path: Path) -> None:
    path = frozen / manifest(frozen)["sources"][0]["retained_path"]
    alternative = tmp_path / "test-only-bytes"
    alternative.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(alternative)
    with pytest.raises(ContractError, match="symlinks"):
        verify(SELECTION, frozen)


@pytest.mark.parametrize("operation", ["verify", "acquire"])
def test_external_manifest_symlink_rejected_without_repair(
    frozen: Path, tmp_path: Path, operation: str
) -> None:
    before = {
        path.relative_to(frozen): path.read_bytes()
        for path in frozen.rglob("*")
        if path.is_file()
    }
    path = frozen / "manifest.json"
    external = tmp_path / "external-valid-manifest.json"
    path.rename(external)
    path.symlink_to(external)

    def no_network(url: str) -> bytes:
        pytest.fail(f"rejected archive must not reacquire {url}")

    with pytest.raises(ContractError, match="frozen paths must not be symlinks"):
        if operation == "verify":
            verify(SELECTION, frozen)
        else:
            acquire(SELECTION, frozen, no_network)

    assert path.is_symlink()
    assert path.readlink() == external
    assert external.read_bytes() == before[Path("manifest.json")]
    assert {
        retained.relative_to(frozen): retained.read_bytes()
        for retained in frozen.rglob("*")
        if retained.is_file()
    } == before
