"""Fictional finalized fixtures only; never approve or score real pilot labels."""

import copy
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.acquisition import digest, record_json
from version_aware_retriever.contracts import (
    ApplicabilityAssertion,
    AssertionKind,
    DocumentType,
    EvidenceRole,
    EvidenceUnit,
    GoldJudgment,
    QueryKind,
    ReviewStatus,
    SelectorKind,
    SourceManifestEntry,
    VersionApplicability,
    VersionSelector,
)
from version_aware_retriever.evaluation import evaluate
from version_aware_retriever.lexical import RetrievalQuery
from version_aware_retriever.pilot_evaluation import (
    DECISIONS,
    FORMAT,
    PATHS,
    PILOT_IDS,
    RUNS,
    Pilot,
    adapt_run,
    load_pilot,
    read_json,
    result_bytes,
    review,
    reviewed_benchmark,
    save_result,
    score,
)


@pytest.fixture
def fictional(tmp_path: Path) -> tuple[Pilot, dict[str, Any], bytes]:
    """Same dimensions and authorized IDs, entirely invented sources/text/labels."""
    version = VersionSelector(kind=SelectorKind.EXACT, scheme="fictional", value="r1")
    content = "Fictional source passage for tests only."
    source = SourceManifestEntry(
        source_id="fictional-source",
        ecosystem_id="fictional",
        document_type=DocumentType.REFERENCE,
        title="Fictional",
        canonical_url="https://example.invalid/fixture",
        snapshot_locator="fixture:r1",
        content_hash=digest(content.encode()),
        document_version=version,
        captured_at=datetime(2026, 1, 1, tzinfo=UTC),
        publisher="Fictional",
        license="test-only",
        transformation_record="none",
    )
    units = [
        EvidenceUnit(
            evidence_id=f"fictional:E{i}",
            source_id=source.source_id,
            ecosystem_id="fictional",
            content=content,
            content_hash=source.content_hash,
            section_path=("Fictional",),
            source_locator="L1-L1",
            applicability=(
                ApplicabilityAssertion(
                    kind=AssertionKind.BEHAVIOR,
                    content_locator="chars:0:10",
                    basis_locator="L1-L1",
                    basis="Fictional assumption",
                    applies_to=(version,),
                ),
            ),
        )
        for i in range(34)
    ]
    public = [
        asdict(
            RetrievalQuery(
                query_id=q,
                ecosystem_id="fictional",
                query_text=f"Fictional question {q}",
                query_kind=QueryKind.LOOKUP,
                source_version=None,
                requested_version=version,
            )
        )
        for q in (
            *PILOT_IDS,
            "fictional:q1",
            "fictional:q2",
            "fictional:q3",
            "fictional:q4",
        )
    ]

    def write(name: str, value: object) -> None:
        path = tmp_path / PATHS[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    write(
        "evidence",
        {
            "units": [
                {"key": f"fictional-{i}", "record": asdict(e)}
                for i, e in enumerate(units)
            ],
            "selection_hash": "fictional",
        },
    )
    write(
        "manifest",
        {"sources": [{"record": record_json(source)}], "selection_hash": "fictional"},
    )
    write("public_queries", public)
    write("labeling_policy", "Fictional labeling policy for tests only")
    eh = digest((tmp_path / PATHS["evidence"]).read_bytes())
    write(
        "development_queries",
        {
            "split": "dev",
            "review_status": "draft",
            "human_review_status": "pending",
            "artifact_bindings": {PATHS["evidence"]: eh},
            "queries": [
                {
                    "retriever_input": row,
                    "curation": {
                        "primary_category": "exact_identifier",
                        "proposed_answerability": "answerable",
                    },
                }
                for row in public
            ],
        },
    )
    proposals = []
    for q in PILOT_IDS:
        for i, e in enumerate(units):
            positive = i == 0 and q != PILOT_IDS[-1]
            wrong = i == 1 and q == PILOT_IDS[0]
            judgment = GoldJudgment(
                query_id=q,
                evidence_id=e.evidence_id,
                topical_relevance=2 if positive or wrong else 0,
                version_applicability=VersionApplicability.VALID
                if positive
                else VersionApplicability.INVALID
                if wrong
                else VersionApplicability.UNKNOWN,
                evidence_roles=(EvidenceRole.REQUESTED_BEHAVIOR,),
                rationale="Fictional draft assumption",
                supporting_locators=("chars:0:10",),
                review_status=ReviewStatus.DRAFT,
                hard_negative=wrong,
            )
            proposals.append(
                {
                    "judgment": asdict(judgment),
                    "human_review_status": "pending",
                    "unresolved_issues": ["Fictional scope issue"]
                    if q == PILOT_IDS[2] and i == 2
                    else [],
                }
            )
    write(
        "pilot",
        {
            "review_status": "draft",
            "human_review_status": "pending",
            "query_ids": PILOT_IDS,
            "artifact_bindings": {
                PATHS["evidence"]: eh,
                PATHS["development_queries"]: digest(
                    (tmp_path / PATHS["development_queries"]).read_bytes()
                ),
            },
            "judgments": proposals,
        },
    )
    pilot = load_pilot(tmp_path)
    decisions = {
        "format": FORMAT,
        "bindings": pilot.bindings,
        "status": "reviewed",
        "unresolved_issues": [],
        "question_decisions": [
            {
                "query_id": q,
                "status": "reviewed",
                "reviewer": "FICTIONAL TEST REVIEWER",
                "answerability": "unanswerable" if q == PILOT_IDS[-1] else "answerable",
                "rationale": "Fictional whole-corpus decision",
                "reviewed_all_evidence": True,
                "supporting_evidence": [
                    {"evidence_id": units[0].evidence_id, "locator": "chars:0:10"}
                ],
                "unresolved_issues": [],
            }
            for q in PILOT_IDS
        ],
        "pair_decisions": [
            {
                "query_id": j.query_id,
                "evidence_id": j.evidence_id,
                "status": "reviewed",
                "reviewer": "FICTIONAL TEST REVIEWER",
                "action": "confirm",
                "correction": {},
                "rationale": "Fictional source-grounded confirmation",
                "supporting_locators": ["chars:0:10"],
                "issue_resolution": "Fictional issue resolved",
                "unresolved_issues": [],
            }
            for j in pilot.proposals
        ],
    }
    ids = [u.evidence_id for u in reversed(units)]
    run = {
        "status": "unscored",
        "run_id": "fictional:run",
        "retrieval_input_snapshot": pilot.snapshot,
        "artifact_hashes": {
            "evidence": pilot.bindings["evidence"],
            "public_queries": pilot.bindings["public_queries"],
        },
        "configuration": {"return_policy": "Fictional full ranking"},
        "results": [{"query_id": q["query_id"], "evidence_ids": ids} for q in public],
        "diagnostics": [
            {"query_id": q["query_id"], "scores": list(range(34))} for q in public
        ],
    }
    body = json.dumps(run).encode()
    for relative in RUNS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    return pilot, decisions, body


def test_pending_partial_and_material_issues(
    fictional: tuple[Pilot, dict[str, Any], bytes],
) -> None:
    pilot, complete, run = fictional
    pending = {
        **complete,
        "status": "pending",
        "question_decisions": [],
        "pair_decisions": [],
    }
    state = review(pilot, pending)[0]
    assert state["question_decisions"] == {"reviewed": 0, "pending": 4}
    assert state["pair_decisions"] == {"reviewed": 0, "pending": 136}
    assert len(state["unresolved_issues"]) == 1
    with pytest.raises(ValueError, match="blocked"):
        score(pilot, pending, (run,))
    pending["question_decisions"] = complete["question_decisions"][:1]
    pending["pair_decisions"] = complete["pair_decisions"][:34]
    assert review(pilot, pending)[0]["pair_decisions"]["pending"] == 102
    with pytest.raises(ValueError, match="blocked"):
        score(pilot, pending, (run,))
    complete["pair_decisions"][0]["unresolved_issues"] = [
        "Fictional material uncertainty"
    ]
    with pytest.raises(ValueError, match="blocked"):
        score(pilot, complete, (run,))
    complete["pair_decisions"][0]["unresolved_issues"] = []
    for decision in complete["pair_decisions"]:
        decision["issue_resolution"] = None
    assert len(review(pilot, complete)[0]["unresolved_issues"]) == 1


def test_complete_matches_evaluator_and_preserves_inputs(
    fictional: tuple[Pilot, dict[str, Any], bytes], tmp_path: Path
) -> None:
    pilot, decisions, body = fictional
    before = copy.deepcopy((pilot, decisions, body))
    files = {
        p: (p.read_bytes(), p.stat().st_mtime_ns)
        for p in tmp_path.rglob("*")
        if p.is_file()
    }
    assert review(pilot, decisions)[0]["scoring_permitted"]
    benchmark = reviewed_benchmark(pilot, decisions)
    adapted = adapt_run(pilot, benchmark, body)
    assert all(
        r.evidence_ids == tuple(json.loads(body)["results"][0]["evidence_ids"])
        for r in adapted.results
    )
    result = score(pilot, decisions, (body,))
    assert result["runs"][0]["evaluation"] == asdict(evaluate(benchmark, adapted))
    assert result == score(pilot, decisions, (body,))
    assert before == (pilot, decisions, body)
    assert files == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in files}
    assert len(benchmark.evidence) == 34 and len(benchmark.judgments) == 136
    assert any(
        j.version_applicability is VersionApplicability.UNKNOWN
        for j in benchmark.judgments
    )


@pytest.mark.parametrize(
    "bad",
    [
        "stale",
        "duplicate-pair",
        "unknown-pair",
        "duplicate-question",
        "unknown-question",
        "contradiction",
        "bad-locator",
        "no-reviewer",
    ],
)
def test_bad_decisions(
    fictional: tuple[Pilot, dict[str, Any], bytes], bad: str
) -> None:
    pilot, decisions, _ = fictional
    if bad == "stale":
        decisions["bindings"] = {**decisions["bindings"], "evidence": "stale"}
    elif bad == "duplicate-pair":
        decisions["pair_decisions"].append(decisions["pair_decisions"][0])
    elif bad == "unknown-pair":
        decisions["pair_decisions"][0]["evidence_id"] = "unknown"
    elif bad == "duplicate-question":
        decisions["question_decisions"].append(decisions["question_decisions"][0])
    elif bad == "unknown-question":
        decisions["question_decisions"][0]["query_id"] = "unknown"
    elif bad == "contradiction":
        decisions["pair_decisions"][0]["correction"] = {"topical_relevance": 1}
    elif bad == "bad-locator":
        decisions["pair_decisions"][0]["supporting_locators"] = ["chars:0:9999"]
    else:
        decisions["pair_decisions"][0]["reviewer"] = ""
    with pytest.raises(ValueError):
        review(pilot, decisions)


def test_explicit_correction_and_answerability_consistency(
    fictional: tuple[Pilot, dict[str, Any], bytes],
) -> None:
    pilot, decisions, body = fictional
    original = reviewed_benchmark(pilot, decisions)
    decisions["question_decisions"][0]["answerability"] = "unanswerable"
    with pytest.raises(ValueError, match="complete reviewed matrix"):
        score(pilot, decisions, (body,))
    pair = decisions["pair_decisions"][0]
    pair["action"] = "correct"
    pair["correction"] = {"topical_relevance": 1, "evidence_roles": ["background"]}
    corrected = reviewed_benchmark(pilot, decisions)
    changed = [
        (a, b)
        for a, b in zip(original.judgments, corrected.judgments, strict=True)
        if a != b
    ]
    assert len(changed) == 1 and changed[0][1].topical_relevance == 1
    assert corrected.benchmark_revision != original.benchmark_revision
    pair["supporting_locators"] = []
    with pytest.raises(ValueError, match="locators"):
        review(pilot, decisions)


@pytest.mark.parametrize(
    "bad",
    [
        "snapshot",
        "hash",
        "missing-query",
        "unknown-evidence",
        "duplicate-evidence",
        "duplicate-query",
        "scores",
    ],
)
def test_bad_saved_run(
    fictional: tuple[Pilot, dict[str, Any], bytes], bad: str
) -> None:
    pilot, decisions, body = fictional
    run = json.loads(body)
    if bad == "snapshot":
        run["retrieval_input_snapshot"] = "stale"
    elif bad == "hash":
        run["artifact_hashes"]["public_queries"] = "stale"
    elif bad == "missing-query":
        run["results"].pop(0)
    elif bad == "unknown-evidence":
        run["results"][0]["evidence_ids"][0] = "unknown"
    elif bad == "duplicate-evidence":
        run["results"][0]["evidence_ids"][0] = run["results"][0]["evidence_ids"][1]
    elif bad == "duplicate-query":
        run["results"][0]["query_id"] = run["results"][1]["query_id"]
    else:
        run["diagnostics"][0]["scores"] = []
    with pytest.raises(ValueError):
        score(pilot, decisions, (json.dumps(run).encode(),))


def test_loader_stale_public_and_duplicate_json(
    fictional: tuple[Pilot, dict[str, Any], bytes], tmp_path: Path
) -> None:
    path = tmp_path / PATHS["public_queries"]
    data = json.loads(path.read_bytes())
    data[0]["query_text"] = "Changed fictional input"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="public/draft"):
        load_pilot(tmp_path)
    path.write_text('{"status":"pending","status":"reviewed"}')
    with pytest.raises(ValueError, match="duplicate JSON"):
        read_json(path)


def test_short_accepted_lists_and_unknown_stays_unknown(
    fictional: tuple[Pilot, dict[str, Any], bytes],
) -> None:
    pilot, decisions, body = fictional
    saved = json.loads(body)
    saved["run_id"] = "fictional:short-list"
    saved["results"][0]["evidence_ids"] = ["fictional:E3", "fictional:E0"]
    saved["diagnostics"][0]["scores"] = [2, 1]
    saved["results"][3]["evidence_ids"] = []
    saved["diagnostics"][3]["scores"] = []
    short = json.dumps(saved).encode()
    result = score(pilot, decisions, (body, short))
    assert result["runs"][1]["adapted_run"]["results"][0]["evidence_ids"] == (
        "fictional:E3",
        "fictional:E0",
    )
    assert result["runs"][1]["evaluation"]["unanswerable_false_positive_rate"] == 0
    pair = decisions["pair_decisions"][0]
    pair["action"] = "correct"
    pair["correction"] = {"version_applicability": "unknown"}
    with pytest.raises(ValueError, match="answerability conflicts"):
        score(pilot, decisions, (body,))
    decisions["question_decisions"][0]["answerability"] = "unanswerable"
    benchmark = reviewed_benchmark(pilot, decisions)
    judgment = next(
        j
        for j in benchmark.judgments
        if (j.query_id, j.evidence_id) == (PILOT_IDS[0], "fictional:E0")
    )
    assert judgment.version_applicability is VersionApplicability.UNKNOWN
    assert not judgment.is_valid_positive


def test_readiness_never_reads_results_or_held_out(
    fictional: tuple[Pilot, dict[str, Any], bytes],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, decisions, _ = fictional
    allowed = {tmp_path / p for p in PATHS.values()}
    original = Path.read_bytes

    def guarded(path: Path) -> bytes:
        assert path in allowed
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    pilot = load_pilot(tmp_path)
    decisions["status"] = "pending"
    decisions["question_decisions"] = []
    decisions["pair_decisions"] = []
    assert not review(pilot, decisions)[0]["scoring_permitted"]


@pytest.mark.parametrize("level", ["top", "question", "incomplete-status"])
def test_additional_review_gates(
    fictional: tuple[Pilot, dict[str, Any], bytes],
    level: str,
) -> None:
    pilot, decisions, body = fictional
    if level == "top":
        decisions["unresolved_issues"] = ["Fictional unresolved policy"]
    elif level == "question":
        decisions["question_decisions"][0]["unresolved_issues"] = [
            "Fictional uncertainty"
        ]
    else:
        decisions["pair_decisions"].pop()
    with pytest.raises(ValueError):
        score(pilot, decisions, (body,))


def test_deterministic_serialization(
    fictional: tuple[Pilot, dict[str, Any], bytes],
    tmp_path: Path,
) -> None:
    pilot, decisions, run = fictional
    decision_bytes = json.dumps(decisions).encode()
    body = result_bytes(pilot, decision_bytes, (run,))
    assert body == result_bytes(pilot, decision_bytes, (run,))
    result = json.loads(body)
    assert result["review_decisions_hash"] == digest(decision_bytes)
    assert result["evaluator"]["cutoffs"] == [1, 3, 5]
    assert result["runs"][0]["original_run_hash"] == digest(run)
    target = tmp_path / "results" / "fictional.json"
    save_result(target, body)
    before = (target.read_bytes(), target.stat().st_mtime_ns)
    save_result(target, body)
    assert before == (target.read_bytes(), target.stat().st_mtime_ns)
    link = tmp_path / "symlink.json"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        save_result(link, body)


def test_explicitly_human_approved_real_batch_read_only(tmp_path: Path) -> None:
    """User-approved batch, not fabricated test approval; no inference or file edits."""
    root = Path(__file__).resolve().parents[1]
    paths = [root / p for p in (*PATHS.values(), DECISIONS, *RUNS)]
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
    pilot = load_pilot(root)
    decisions = read_json(root / DECISIONS)
    state = review(pilot, decisions)[0]
    assert state["scoring_permitted"]
    assert state["question_decisions"] == {"reviewed": 4, "pending": 0}
    assert state["pair_decisions"] == {"reviewed": 136, "pending": 0}
    assert state["unresolved_issues"] == []
    assert pilot.bindings["pilot"] == (
        "sha256:ea6c78d733ee5ce4a1d565e7e7fb72d8165e229f1df3ab756fea3f5d881cf7ca"
    )
    benchmark = reviewed_benchmark(pilot, decisions)
    proposals = {(j.query_id, j.evidence_id): j for j in pilot.proposals}
    policy_b = (
        "q:7bd4",
        "evidence:de3bf67621ae0433616b3b88bbad1052768664fea091db62c16a5f92c19fd83b",
    )
    for judgment in benchmark.judgments:
        pair = (judgment.query_id, judgment.evidence_id)
        old = proposals[pair]
        assert old.review_status is ReviewStatus.DRAFT
        assert judgment.review_status is ReviewStatus.REVIEWED
        if pair == policy_b:
            assert judgment.topical_relevance == 1
            assert judgment.version_applicability is VersionApplicability.VALID
            assert judgment.evidence_roles == (EvidenceRole.BACKGROUND,)
            assert not judgment.hard_negative
        else:
            for field in (
                "topical_relevance",
                "version_applicability",
                "evidence_roles",
                "hard_negative",
            ):
                assert getattr(judgment, field) == getattr(old, field)
    assert {q.query_id: q.answerability.value for q in benchmark.queries} == {
        "q:a7c2": "answerable",
        "q:39fa": "answerable",
        "q:7bd4": "answerable",
        "q:b503": "unanswerable",
    }
    assert {
        q: sum(j.query_id == q and j.is_valid_positive for j in benchmark.judgments)
        for q in PILOT_IDS
    } == {"q:a7c2": 2, "q:39fa": 3, "q:7bd4": 1, "q:b503": 0}
    bodies = tuple((root / p).read_bytes() for p in RUNS)
    body = result_bytes(pilot, (root / DECISIONS).read_bytes(), bodies)
    report = json.loads(body)
    for original, retained in zip(bodies, report["runs"], strict=True):
        adapted = adapt_run(pilot, benchmark, original)
        original_results = {
            r["query_id"]: tuple(r["evidence_ids"])
            for r in json.loads(original)["results"]
        }
        assert all(
            r.evidence_ids == original_results[r.query_id] for r in adapted.results
        )
        assert retained["evaluation"] == json.loads(
            json.dumps(asdict(evaluate(benchmark, adapted)))
        )
    assert body == result_bytes(pilot, (root / DECISIONS).read_bytes(), bodies)
    save_result(tmp_path / "real-format-result-copy.json", body)
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
