"""Byte-identity and installed-resource boundary checks; no neural/API calls."""

from importlib.resources import files
from pathlib import Path

import pytest

from version_aware_retriever import grounded_answer as ga
from version_aware_retriever.acquisition import digest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name", tuple(ga.PINS))
def test_bundled_inputs_are_canonical(name: str) -> None:
    bundled = files("version_aware_retriever").joinpath("runtime", Path(name).name)
    assert bundled.read_bytes() == (ROOT / name).read_bytes()
    assert digest(bundled.read_bytes()) == ga.PINS[name]


@pytest.mark.parametrize(
    "release,commit",
    [
        ("1.10.13", "8822578619bf8d0bb754b1cf7a2a905b50240d01"),
        ("2.5.3", "9f58e785a5f1f2c34437f6e9b6adcd5b969e0df4"),
    ],
)
def test_upstream_license_bytes(release: str, commit: str) -> None:
    bundled = files("version_aware_retriever").joinpath(
        "runtime", f"pydantic-{release}-LICENSE"
    )
    canonical = ROOT / "data/pydantic/frozen/licenses" / commit / "LICENSE"
    assert bundled.read_bytes() == canonical.read_bytes()


def test_bundled_projection_matches_checkout() -> None:
    assert ga.load_corpus() == ga.load_corpus(ROOT)


def test_default_corpus_ignores_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = ga.load_corpus(ROOT)
    monkeypatch.chdir(tmp_path)
    original = Path.read_bytes
    allowed = {
        Path(str(files("version_aware_retriever").joinpath("runtime", Path(n).name)))
        for n in ga.PINS
    }

    def guarded(path: Path) -> bytes:
        assert path in allowed
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    assert ga.load_corpus() == expected


def test_explicit_bad_root_does_not_fallback(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ga.load_corpus(tmp_path)


def test_cli_default_is_bundled(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def load(root: Path | None) -> tuple[ga.RetrievedEvidence, ...]:
        assert root is None
        raise ValueError("test reached bundled corpus")

    monkeypatch.setattr(ga, "load_corpus", load)
    monkeypatch.setattr(
        "sys.argv", ["version-aware-retriever", "--query", "Widget?", "--context-only"]
    )
    with pytest.raises(SystemExit) as error:
        ga.main()
    assert error.value.code == 2
    assert "test reached bundled corpus" in capsys.readouterr().err


def test_runtime_resource_allowlist() -> None:
    resources = files("version_aware_retriever").joinpath("runtime")
    assert {p.name for p in resources.iterdir()} == {
        "evidence.json",
        "manifest.json",
        "NOTICE.md",
        "pydantic-1.10.13-LICENSE",
        "pydantic-2.5.3-LICENSE",
    }
