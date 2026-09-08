"""Focused documentation/metadata invariants; no external services or models."""

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pep639_license_metadata() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = metadata["project"]
    assert project["version"] == "0.1.2"
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert "setuptools>=77" in metadata["build-system"]["requires"]
    assert not any(c.startswith("License ::") for c in project.get("classifiers", []))


def test_frozen_constraints_match_recorded_neural_runs() -> None:
    constraints = dict(
        line.split("==")
        for line in (ROOT / "constraints/frozen-eval.txt").read_text().splitlines()
        if line and not line.startswith("#")
    )
    runs = ROOT / "data/pydantic/runs"
    dense = json.loads((runs / "dense.eval.unscored.json").read_text())["runtime"]
    cross = json.loads(
        (runs / "cross-encoder-reranked.eval.unscored.json").read_text()
    )["runtime"]
    assert constraints == dense["packages"]
    assert cross["packages"].items() <= constraints.items()
    assert dense["python"] == cross["python"] == "3.12.7"


def test_canonical_documentation_links_resolve() -> None:
    for name in ("README.md", "docs/README.md", "docs/ARCHITECTURE.md"):
        path = ROOT / name
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^\s)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            destination = (path.parent / target.split("#", 1)[0]).resolve()
            assert destination.is_relative_to(ROOT)
            assert destination.is_file(), (name, target)
