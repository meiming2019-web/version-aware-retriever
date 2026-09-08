"""Offline installed-wheel integrity check; no encoder, generation or gold."""

import argparse
import importlib.metadata
import json
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forbid-root", type=Path, required=True)
    args = parser.parse_args()
    forbidden = args.forbid_root.resolve()
    assert sys.prefix != sys.base_prefix, "use a clean virtual environment"
    assert not Path.cwd().resolve().is_relative_to(forbidden), "leave the checkout"
    resources: set[str] = set()

    def audit(event: str, values: tuple[object, ...]) -> None:
        if event == "socket.connect":
            raise AssertionError("package smoke must not access the network")
        if event == "open" and isinstance(values[0], (str, bytes)):
            path = Path(os.fsdecode(values[0])).resolve()
            assert not path.is_relative_to(forbidden), "unexpected checkout read"
            if path.parent.name == "runtime":
                resources.add(path.name)

    sys.addaudithook(audit)
    from version_aware_retriever import grounded_answer

    assert (
        Path(grounded_answer.__file__)
        .resolve()
        .is_relative_to(Path(sys.prefix).resolve())
    ), "package must come from the clean environment, not the checkout"
    installed = importlib.metadata.distribution("version-aware-retriever")
    assert installed.metadata["License-Expression"] == "MIT"
    assert installed.metadata.get_all("License-File") == ["LICENSE"]
    assert installed.files is not None
    assert not any(
        part in str(name)
        for name in installed.files
        for part in ("benchmark/", "review-decisions", "/results/", "/runs/")
    ), "benchmark artifacts must not be installed"
    # Reuse production parsing, input/content hashes and provenance validation.
    corpus = grounded_answer.load_corpus()
    assert resources == {"evidence.json", "manifest.json"}
    print(
        json.dumps(
            {
                "version": installed.version,
                "license": "MIT",
                "evidence_units": len(corpus),
                "resources": sorted(resources),
                "checkout_reads": 0,
                "network_connections": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
