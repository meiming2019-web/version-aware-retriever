# Frozen runtime data

evidence.json and manifest.json are byte-exact copies of the canonical files at
data/pydantic/extraction/derived/evidence.json and data/pydantic/frozen/manifest.json.
They are release resources, not an independently edited corpus. Tests compare
both bytes and pinned SHA-256 hashes. To update an authorized corpus revision,
copy canonical bytes and update the explicit runtime pins in a new release;
never edit these copies independently. v0.1.0's corpus is frozen.

The evidence contains excerpts from Pydantic documentation, including examples,
at releases 1.10.13 and 2.5.3. The manifest preserves upstream titles, URLs, commit
IDs and provenance. Pydantic's original MIT notices are retained verbatim in
pydantic-1.10.13-LICENSE and pydantic-2.5.3-LICENSE. These notices apply to the
upstream material, not a newly declared license for this project's own code.

Benchmark gold, review sidecars, experiment runs/results, raw source archives,
private certificates and model weights are not bundled in the wheel. The source
distribution includes the reproducibility records used by tests and reports.
