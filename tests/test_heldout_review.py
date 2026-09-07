"""Draft inventory and review gating only; no retrieval/model/results needed."""

import copy
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from version_aware_retriever.acquisition import digest
from version_aware_retriever.contracts import VersionApplicability
from version_aware_retriever.heldout_review import (
    DECISIONS,
    PATHS,
    contamination_guard,
    load_heldout,
    readiness,
)
from version_aware_retriever.pilot_evaluation import review


@pytest.fixture
def root(tmp_path: Path) -> Path:
    original = Path(__file__).resolve().parents[1]
    for name in (*PATHS.values(), DECISIONS):
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((original / name).read_bytes())
    side = tmp_path / DECISIONS
    pending = json.loads(side.read_bytes())
    pending.update(status="pending", question_decisions=[], pair_decisions=[])
    side.write_text(json.dumps(pending))
    return tmp_path


def test_pending_inventory_and_guarded_reads(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    read = Path.read_bytes
    allowed = {root / p for p in (*PATHS.values(), DECISIONS)}
    before = {p: (read(p), p.stat().st_mtime_ns) for p in allowed}

    def guarded(p: Path) -> bytes:
        assert p in allowed, f"Forbidden retrieval/result input: {p}"
        return read(p)

    monkeypatch.setattr(Path, "read_bytes", guarded)
    pilot, draft = load_heldout(root)
    assert len(pilot.public) == 16 and len(pilot.proposals) == 544
    assert all(not j.is_valid_positive for j in pilot.proposals)
    assert (
        sum(
            j.topical_relevance == 2 and j.version_applicability.value == "valid"
            for j in pilot.proposals
        )
        == 28
    )
    assert sum(j.hard_negative for j in pilot.proposals) == 1
    assert (
        sum(
            q["proposed_answerability"] == "answerable"
            for q in draft["question_proposals"]
        )
        == 12
    )
    report = readiness(root)
    assert report["question_decisions"] == {"reviewed": 0, "pending": 16}
    assert report["pair_decisions"] == {"reviewed": 0, "pending": 544}
    assert len(report["unresolved_issues"]) == 1
    assert not report["gold_ready"] and not report["scoring_permitted"]
    assert before == {p: (read(p), p.stat().st_mtime_ns) for p in allowed}
    assert not (root / "data/pydantic/runs").exists()
    assert not (root / "data/pydantic/results").exists()


def test_contamination_stops_before_reads(
    root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unexpected = root / "data/pydantic/runs/bm25.eval.unscored.json"
    unexpected.parent.mkdir(parents=True)
    unexpected.write_text("Do not open this synthetic sentinel.")

    def forbidden(p: Path) -> bytes:
        raise AssertionError(f"Read before contamination check: {p}")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="contamination risk"):
        readiness(root)
    with pytest.raises(ValueError, match="contamination risk"):
        contamination_guard(root)


@pytest.mark.parametrize(
    "change",
    ["missing", "duplicate", "enum", "reviewed", "unknown_id", "answerability"],
)
def test_bad_draft_rejected(root: Path, change: str) -> None:
    p = root / PATHS["draft"]
    d = json.loads(p.read_bytes())
    if change == "missing":
        d["judgments"].pop()
    elif change == "duplicate":
        d["judgments"][-1] = d["judgments"][0]
    elif change == "enum":
        d["judgments"][0]["judgment"]["version_applicability"] = "maybe"
    elif change == "reviewed":
        d["judgments"][0]["judgment"]["review_status"] = "reviewed"
    elif change == "unknown_id":
        d["judgments"][0]["judgment"]["evidence_id"] = "e:unknown"
    else:
        d["question_proposals"][0]["proposed_answerability"] = "unanswerable"
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError):
        load_heldout(root)


def test_stale_sidecar_and_question_revision(root: Path) -> None:
    p = root / DECISIONS
    d = json.loads(p.read_bytes())
    d["bindings"]["draft"] = "stale"
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError, match="stale review"):
        readiness(root)
    q = root / PATHS["evaluation_queries"]
    q.write_bytes(q.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="authored held-out revision"):
        load_heldout(root)


def test_family_leakage_even_with_rebound_draft(root: Path) -> None:
    p = root / PATHS["development_queries"]
    d = json.loads(p.read_bytes())
    d["queries"][0]["curation"]["change_family"] = "required_nullable"
    p.write_text(json.dumps(d))
    proposal = root / PATHS["draft"]
    data = json.loads(proposal.read_bytes())
    data["artifact_bindings"][PATHS["development_queries"]] = digest(p.read_bytes())
    proposal.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="change_family leakage"):
        load_heldout(root)


def test_complete_explicit_synthetic_gate_and_missing_decisions(root: Path) -> None:
    """In-memory fictional questions/labels; never promote or save real judgments."""
    original, _ = load_heldout(root)
    ids = {q.query_id: f"q:fictional-{i}" for i, q in enumerate(original.public)}
    public = tuple(
        replace(q, query_id=ids[q.query_id], query_text="Fictional fixture only")
        for q in original.public
    )
    proposals = tuple(
        replace(
            j,
            query_id=ids[j.query_id],
            topical_relevance=0,
            version_applicability=VersionApplicability.UNKNOWN,
            hard_negative=False,
        )
        for j in original.proposals
    )
    pilot = replace(
        original,
        public=public,
        proposals=proposals,
        curation={ids[k]: v for k, v in original.curation.items()},
        issues={(j.query_id, j.evidence_id): [] for j in proposals},
    )
    decisions: dict[str, Any] = {
        "format": "heldout-review-v1",
        "status": "reviewed",
        "bindings": pilot.bindings,
        "unresolved_issues": [],
        "question_decisions": [
            {
                "query_id": q.query_id,
                "status": "reviewed",
                "reviewer": "Synthetic fixture, not a human sign-off",
                "answerability": "unanswerable",
                "rationale": "Fictional absent fact",
                "reviewed_all_evidence": True,
                "supporting_evidence": [],
                "unresolved_issues": [],
            }
            for q in public
        ],
        "pair_decisions": [
            {
                "query_id": j.query_id,
                "evidence_id": j.evidence_id,
                "status": "reviewed",
                "reviewer": "Synthetic fixture, not a human sign-off",
                "action": "confirm",
                "correction": {},
                "rationale": "Fictional unrelated pair",
                "supporting_locators": list(j.supporting_locators),
                "issue_resolution": None,
                "unresolved_issues": [],
            }
            for j in proposals
        ],
    }
    assert review(pilot, decisions, heldout=True)[0]["scoring_permitted"]
    for field in ("question_decisions", "pair_decisions"):
        partial = copy.deepcopy(decisions)
        partial["status"] = "pending"
        partial[field].pop()
        assert not review(pilot, partial, heldout=True)[0]["scoring_permitted"]
    issue_pair = (proposals[0].query_id, proposals[0].evidence_id)
    disputed = replace(
        pilot, issues={**pilot.issues, issue_pair: ["Fictional scope issue"]}
    )
    assert not review(disputed, decisions, heldout=True)[0]["scoring_permitted"]
    resolved = copy.deepcopy(decisions)
    resolved["pair_decisions"][0]["issue_resolution"] = "Fictional explicit resolution"
    assert review(disputed, resolved, heldout=True)[0]["scoring_permitted"]
