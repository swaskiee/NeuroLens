"""
Tests for the NeuroLens Cognitive Compiler.

These test behaviour (structure, deadline handling, ambiguity logic, fallback and
validation paths), not fixed answer strings. No test needs a running model or
network: the rule-based engine is tested directly, and the model path is tested
with a stubbed `_call_model`.
"""
import json

import pytest

from cognitive_compiler import (
    CognitiveCompiler,
    NeuroLensInsight,
    detect_ambiguity_signals,
    extract_deterministic_deadlines,
)

MEETING = (
    "It would probably be good if you could get the analysis over to me sometime before Friday. "
    "And maybe revisit the first section because I don't think we're quite there yet."
)


@pytest.fixture
def rules():
    return CognitiveCompiler(use_model=False)


# ---- deadline extraction -----------------------------------------------------
def test_weekday_deadline():
    assert extract_deterministic_deadlines("Send it by Friday morning") == ["Friday"]


def test_soft_weekday_deadline_is_not_duplicated():
    assert extract_deterministic_deadlines("get it to me sometime before Friday") == ["Friday"]


def test_relative_and_clock_deadlines():
    assert extract_deterministic_deadlines("Please finish this tomorrow") == ["Tomorrow"]
    assert extract_deterministic_deadlines("Submit the report before 5 pm") == ["5 PM"]
    assert extract_deterministic_deadlines("Kal tak bana dena") == ["Tomorrow (kal tak)"]


def test_no_deadline_when_none_stated():
    assert extract_deterministic_deadlines("Maybe we should look into that") == []


# ---- ambiguity signals ---------------------------------------------------------
def test_ambiguity_signal_detection():
    signals = detect_ambiguity_signals("Maybe we could look into that sometime soon")
    assert {"maybe", "look into", "sometime", "soon"} <= set(signals)


def test_word_boundaries_prevent_false_hits():
    # 'take' contains 'tak'; 'banana' contains 'bana'. Neither may trigger anything.
    assert detect_ambiguity_signals("I will take a banana") == []


# ---- rule-based compilation ------------------------------------------------------
def test_meeting_structure(rules):
    insight = rules.compile(MEETING)
    assert isinstance(insight, NeuroLensInsight)
    assert len(insight.actions) == 2
    assert "analysis" in insight.actions[0].task.lower()
    assert "first section" in insight.actions[1].task.lower()
    assert [d.deadline for d in insight.deadlines] == ["Friday"]  # exactly once
    assert insight.actions[0].priority == "high"  # has a deadline in its clause
    assert insight.ambiguity.level == "medium"
    assert insight.clarifying_question
    assert all(p.confidence_basis.startswith("heuristic") for p in insight.possible_interpretations)


def test_ambiguous_statement_asks_instead_of_guessing(rules):
    insight = rules.compile("Maybe we should look into that sometime soon.")
    assert insight.actions == []
    assert insight.deadlines == []
    assert insight.ambiguity.level == "high"
    assert "'that'" in insight.clarifying_question


def test_hinglish_actions_and_deadline(rules):
    insight = rules.compile(
        "Kal tak presentation ka architecture slide bana dena, aur jo first section hai na usko thoda simple kar dena."
    )
    assert len(insight.actions) == 2
    assert "architecture slide" in insight.actions[0].task
    assert [d.deadline for d in insight.deadlines] == ["Tomorrow (kal tak)"]


def test_plain_english_containing_tak_is_not_treated_as_hinglish(rules):
    insight = rules.compile("Can you take care of that?")
    assert "architecture" not in insight.literal_meaning
    assert insight.ambiguity.level != "low"
    assert "'that'" in insight.clarifying_question


def test_missing_deadline_is_reported(rules):
    insight = rules.compile("Please update the dashboard.")
    assert insight.actions and not insight.deadlines
    assert "A deadline" in insight.ambiguity.missing_information


def test_provenance_never_claims_npu(rules):
    insight = rules.compile(MEETING)
    assert "npu" not in insight.runtime_provenance.lower()
    assert "rule-based" in insight.runtime_provenance.lower()


# ---- model path (stubbed, no network) --------------------------------------------
VALID_MODEL_JSON = {
    "literal_meaning": "Send the report by Friday.",
    "actions": [{"task": "Send the report", "priority": "high", "owner": "unknown"}],
    "deadlines": [],
    "possible_interpretations": [
        {"interpretation": "A firm request", "confidence": 0.8, "evidence": "by Friday"}
    ],
    "ambiguity": {"level": "low", "reason": "explicit", "missing_information": []},
    "clarifying_question": None,
    "suggested_replies": ["Will do."],
}


def test_valid_model_output_is_used_and_enriched(monkeypatch):
    c = CognitiveCompiler()
    monkeypatch.setattr(c, "_call_model", lambda text: ("```json\n" + json.dumps(VALID_MODEL_JSON) + "\n```", ""))
    insight = c.compile("Send the report by Friday")
    assert insight.runtime_provenance.startswith("Local model")
    assert [d.deadline for d in insight.deadlines] == ["Friday"]  # added by rule cross-check
    assert insight.deadlines[0].detected_via == "deterministic_rule"


def test_invalid_model_output_falls_back_and_says_so(monkeypatch):
    c = CognitiveCompiler()
    monkeypatch.setattr(c, "_call_model", lambda text: ("not json at all", ""))
    insight = c.compile("Send the report by Friday")
    assert "failed schema validation" in insight.runtime_provenance


def test_schema_violation_falls_back(monkeypatch):
    bad = dict(VALID_MODEL_JSON, actions=[{"task": "x", "priority": "urgent!!"}])
    c = CognitiveCompiler()
    monkeypatch.setattr(c, "_call_model", lambda text: (json.dumps(bad), ""))
    assert "failed schema validation" in c.compile("Send the report by Friday").runtime_provenance


def test_unreachable_endpoint_falls_back():
    c = CognitiveCompiler(endpoint_url="http://127.0.0.1:9/v1", timeout=0.5)
    insight = c.compile("Send the report by Friday")
    assert "unreachable" in insight.runtime_provenance
    assert insight.actions
